"""
SwiftVisa - Visa Document Chunking Script
Processes visa policy documents for one or more countries and prepares them for vector storage
"""

import os
import re
from pathlib import Path
from typing import List
import json

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

# Visa type keywords used to infer visa categories from file names and content.
# Covers all four supported countries: UK, Canada, Australia, New Zealand.
DEFAULT_VISA_TYPES = {

    # ── United Kingdom ────────────────────────────────────────────────────────
    "student": [
        "student_visa", "tier_4", "student route", "student visa",
    ],
    "graduate": [
        "graduate_visa", "graduate route", "post-study", "graduate visa",
    ],
    "skilled_worker": [
        "skilled_worker", "tier_2", "skilled worker visa", "skilled worker route",
    ],
    "health_care_worker": [
        "health_care_worker", "health and care", "nhs", "health care worker",
    ],
    "visitor": [
        "standard_visitor", "standard visitor", "tourist visa", "visitor visa",
    ],

    # ── Canada ────────────────────────────────────────────────────────────────
    "student_permit": [
        "student permit", "study permit", "designated learning institution", "dli",
    ],
    "work_permit": [
        "work permit", "lmia", "labour market impact assessment", "temporary foreign worker",
    ],
    "express_entry": [
        "express entry", "federal skilled worker", "canadian experience class",
        "federal skilled trades", "comprehensive ranking system", "crs",
    ],
    "visitor_visa": [
        "temporary resident visa", "trv", "eta", "electronic travel authorisation",
        "visitor visa canada",
    ],
    "post_graduation_work_permit": [
        "post-graduation work permit", "pgwp", "post graduation work permit",
    ],

    # ── Australia ─────────────────────────────────────────────────────────────
    "student_visa_500": [
        "subclass 500", "student visa 500", "cricos", "oshc",
        "overseas student health cover", "genuine temporary entrant",
    ],
    "temporary_graduate_visa_485": [
        "subclass 485", "temporary graduate", "graduate work stream",
        "post-study work stream", "485",
    ],
    "skilled_nominated_visa_190": [
        "subclass 190", "skilled nominated", "state nomination", "190 visa",
        "skilled occupation list",
    ],
    "temporary_skill_shortage_visa_482": [
        "subclass 482", "temporary skill shortage", "tss visa", "482 visa",
        "tsmit", "stsol", "mltssl",
    ],
    "visitor_visa_600": [
        "subclass 600", "visitor visa 600", "tourist stream", "600 visa",
        "genuine temporary entrant australia",
    ],

    # ── New Zealand ───────────────────────────────────────────────────────────
    "student_visa": [
        "new zealand student visa", "nz student visa", "nzqa", "student visa nz",
    ],
    "post_study_work_visa": [
        "post study work", "post-study work visa", "psw visa new zealand",
    ],
    "skilled_migrant_category": [
        "skilled migrant category", "skilled migrant", "expression of interest nz",
        "eoi new zealand",
    ],
    "accredited_employer_work_visa": [
        "accredited employer work visa", "aewv", "job check", "median wage nz",
        "accredited employer",
    ],
    "visitor_visa": [
        "new zealand visitor visa", "nz visitor visa", "nzeta", "visitor visa nz",
    ],
}


class VisaDocumentChunker:
    """Handles chunking of visa policy documents for all supported countries."""

    def __init__(self, data_path: str = "KB"):
        self.data_path = Path(data_path)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1200,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", ". ", ", ", " ", ""]
        )

    def _normalize_country_name(self, raw_name: str) -> str:
        cleaned = raw_name.lower()
        cleaned = re.sub(r"[_\-]+", " ", cleaned)
        cleaned = re.sub(r"\s+policies?$", "", cleaned)
        cleaned = cleaned.strip()
        return " ".join(word.capitalize() for word in cleaned.split()) if cleaned else "Unknown"

    def _infer_country_name(self, folder: Path) -> str:
        return self._normalize_country_name(folder.name)

    def _discover_pdf_paths(self) -> List[Path]:
        if not self.data_path.exists():
            return []
        if self.data_path.is_file() and self.data_path.suffix.lower() == ".pdf":
            return [self.data_path]
        return sorted([p for p in self.data_path.rglob("*.pdf") if p.is_file()])

    def load_documents(self) -> List:
        """Load all PDF policy documents from the configured data path."""
        print(f" Loading documents from: {self.data_path}")

        if not self.data_path.exists():
            print(f" Path not found: {self.data_path} — creating directory...")
            os.makedirs(self.data_path, exist_ok=True)
            return []

        pdf_paths = self._discover_pdf_paths()
        if not pdf_paths:
            return []

        documents = []
        for path in pdf_paths:
            try:
                loader = PyPDFLoader(str(path))
                loaded_docs = loader.load()
            except Exception as exc:
                print(f" Failed to load {path}: {exc}")
                continue

            country = self._infer_country_name(path.parent)
            for doc in loaded_docs:
                doc.metadata["source"] = str(path)
                doc.metadata["source_file"] = path.name
                doc.metadata["country"] = country
                documents.append(doc)

        print(f" Loaded {len(documents)} pages from {len(pdf_paths)} PDF(s)")
        return documents

    def extract_visa_type(self, doc) -> str:
        """
        Infer a visa type from the document's filename and content.

        Matching priority:
          1. Filename stem (most reliable — policy files are typically named by visa)
          2. First 1000 chars of content
          3. Full source path

        Longer / more specific keywords are checked before shorter ones to
        avoid 'visitor' matching before 'visitor_visa_600', for example.
        """
        source = str(doc.metadata.get("source", "")).lower()
        filename = Path(source).stem.lower()
        content_head = doc.page_content[:1000].lower()

        # Sort visa types so longer/more-specific keyword strings win
        sorted_types = sorted(
            DEFAULT_VISA_TYPES.items(),
            key=lambda item: max(len(kw) for kw in item[1]),
            reverse=True,
        )

        for visa_type, keywords in sorted_types:
            for kw in keywords:
                if kw in filename or kw in content_head or kw in source:
                    return visa_type

        # Fallback: slugify the filename
        fallback = re.sub(r"[^a-z0-9]+", "_", filename).strip("_")
        return fallback or "general"

    def chunk_documents(self, documents: List) -> List:
        """Split documents into searchable chunks with metadata."""
        print(f"\n  Chunking {len(documents)} document pages...")

        all_chunks = []
        for doc in documents:
            splits = self.text_splitter.split_documents([doc])
            visa_type = self.extract_visa_type(doc)
            country = doc.metadata.get("country", "Unknown")
            source_file = os.path.basename(doc.metadata.get("source", ""))

            for i, split in enumerate(splits):
                split.metadata.update({
                    "country":      country,
                    "visa_type":    visa_type,
                    "source_file":  source_file,
                    "chunk_id":     i,
                    "total_chunks": len(splits),
                })
                all_chunks.append(split)

        print(f" Created {len(all_chunks)} chunks")
        return all_chunks

    def analyze_chunks(self, chunks: List):
        """Print chunk statistics."""
        if not chunks:
            print("  No chunks to analyze")
            return

        lengths = [len(c.page_content) for c in chunks]
        print(f"\n Chunk Analysis:")
        print("=" * 60)
        print(f"  Total chunks    : {len(chunks)}")
        print(f"  Avg chunk size  : {sum(lengths)/len(lengths):.0f} chars")
        print(f"  Min / Max       : {min(lengths)} / {max(lengths)} chars")

        print("\n  By Country:")
        country_counts: dict = {}
        for c in chunks:
            k = c.metadata.get("country", "Unknown")
            country_counts[k] = country_counts.get(k, 0) + 1
        for k, v in sorted(country_counts.items()):
            print(f"    {k}: {v}")

        print("\n  By Visa Type:")
        visa_counts: dict = {}
        for c in chunks:
            k = c.metadata.get("visa_type", "unknown")
            visa_counts[k] = visa_counts.get(k, 0) + 1
        for k, v in sorted(visa_counts.items()):
            print(f"    {k.replace('_', ' ').title()}: {v}")

        print("\n  Sample Chunk:")
        print("-" * 60)
        sample = chunks[0]
        print(f"  Content : {sample.page_content[:300]}...")
        print(f"  Metadata: {json.dumps(sample.metadata, indent=4)}")
        print("-" * 60)

    def save_chunks_json(self, chunks: List, output_path: str = "chunks_preview.json"):
        """Save chunks to JSON for inspection."""
        data = [{"content": c.page_content, "metadata": c.metadata} for c in chunks]
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\n Chunks saved to: {output_path}")

    def process_all(self) -> List:
        """Complete pipeline: load → chunk → analyze → save preview."""
        print(" Starting visa policy document processing...")
        print("=" * 60)

        documents = self.load_documents()
        if not documents:
            print(f"\n  No documents found under: {self.data_path}")
            if self.data_path.exists():
                children = sorted(
                    [i.name for i in self.data_path.iterdir() if i.is_dir()]
                )
                if children:
                    print("\n  Found country folders:")
                    for name in children:
                        print(f"    {name}")
                    print("\n  Add policy PDFs inside those folders and re-run.")
            return []

        chunks = self.chunk_documents(documents)
        self.analyze_chunks(chunks)
        self.save_chunks_json(chunks)

        print("\n Processing complete!")
        return chunks


def main():
    chunker = VisaDocumentChunker(data_path="KB")
    return chunker.process_all()


if __name__ == "__main__":
    chunks = main()