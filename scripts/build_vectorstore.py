"""
SwiftVisa - FAISS Vector Store Builder (Multi-Country)
Builds a separate FAISS index per country from that country's policy documents.

Usage:
    python build_vectorstore.py              # build all countries
    python build_vectorstore.py --country uk # build one country
"""

import os
import sys
import json
import pickle
import logging
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import numpy as np

from sentence_transformers import SentenceTransformer
import faiss

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))
from chunk_documents import VisaDocumentChunker
from utils.Country_config import COUNTRY_CONFIG, get_vectorstore_path, get_data_dir

# ── Logging ───────────────────────────────────────────────────────────────────
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/vectorstore_build.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class VectorStoreBuilder:
    """Builds a FAISS vector store for a single country."""

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        model_cache_dir: str = "models/sentence_transformer",
    ):
        os.makedirs(model_cache_dir, exist_ok=True)
        logger.info(f"[MODEL] Loading embedding model: {model_name}")
        self.model_name = model_name
        self.embedding_model = SentenceTransformer(model_name, cache_folder=model_cache_dir)
        self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
        logger.info(f"[OK] Embedding dim: {self.embedding_dim}")

    # ── Core helpers ──────────────────────────────────────────────────────────

    def create_embeddings(self, chunks: List) -> np.ndarray:
        texts = [c.page_content for c in chunks]
        logger.info(f"[EMBED] Encoding {len(texts)} chunks...")
        embeddings = self.embedding_model.encode(
            texts, show_progress_bar=True, batch_size=32, convert_to_numpy=True
        )
        logger.info(f"[OK] Embeddings shape: {embeddings.shape}")
        return embeddings

    def build_faiss_index(self, embeddings: np.ndarray) -> faiss.Index:
        logger.info("[INDEX] Building FAISS index...")
        faiss.normalize_L2(embeddings)
        index = faiss.IndexFlatIP(self.embedding_dim)
        index.add(embeddings)
        logger.info(f"[OK] Vectors in index: {index.ntotal}")
        return index

    def save_vectorstore(
        self, index: faiss.Index, chunks: List, vectorstore_path: str, metadata: Dict
    ):
        os.makedirs(vectorstore_path, exist_ok=True)

        # FAISS index
        index_file = os.path.join(vectorstore_path, "index.faiss")
        faiss.write_index(index, index_file)
        logger.info(f"[SAVE] FAISS index → {index_file}")

        # Chunk metadata (pickle)
        chunks_meta = [
            {"id": i, "content": c.page_content, "metadata": c.metadata}
            for i, c in enumerate(chunks)
        ]
        pkl_file = os.path.join(vectorstore_path, "index.pkl")
        with open(pkl_file, "wb") as f:
            pickle.dump(chunks_meta, f)
        logger.info(f"[SAVE] Chunks pickle → {pkl_file}")

        # Human-readable build info
        build_info = {
            "build_date": datetime.now().isoformat(),
            "model_name": self.model_name,
            "embedding_dim": self.embedding_dim,
            "total_chunks": len(chunks),
            "total_vectors": index.ntotal,
            **metadata,
        }
        meta_file = os.path.join(vectorstore_path, "metadata.json")
        with open(meta_file, "w") as f:
            json.dump(build_info, f, indent=2)
        logger.info(f"[SAVE] Metadata → {meta_file}")

    def load_vectorstore(self, vectorstore_path: str):
        """Load an existing index. Returns (index, chunks_meta) or (None, None)."""
        index_file = os.path.join(vectorstore_path, "index.faiss")
        pkl_file = os.path.join(vectorstore_path, "index.pkl")

        if not (os.path.exists(index_file) and os.path.exists(pkl_file)):
            logger.error(f"[ERROR] Vector store not found at {vectorstore_path}")
            return None, None

        index = faiss.read_index(index_file)
        with open(pkl_file, "rb") as f:
            chunks_meta = pickle.load(f)
        logger.info(f"[LOAD] {index.ntotal} vectors, {len(chunks_meta)} chunks from {vectorstore_path}")
        return index, chunks_meta

    def test_search(
        self,
        index: faiss.Index,
        chunks_meta: List,
        query: str,
        k: int = 3,
    ):
        q_emb = self.embedding_model.encode([query], convert_to_numpy=True)
        faiss.normalize_L2(q_emb)
        distances, indices = index.search(q_emb, k)

        print(f"\n{'='*70}")
        print(f"Query: {query}")
        print(f"{'='*70}")
        for rank, (idx, dist) in enumerate(zip(indices[0], distances[0]), 1):
            chunk = chunks_meta[idx]
            print(f"\n[{rank}] Similarity: {dist:.4f}")
            print(f"  Visa type : {chunk['metadata'].get('visa_type', 'N/A')}")
            print(f"  Source    : {chunk['metadata'].get('source_file', 'N/A')}")
            print(f"  Excerpt   : {chunk['content'][:280]}...")
            print("-" * 70)

    # ── Per-country pipeline ──────────────────────────────────────────────────

    def build_for_country(self, country_code: str) -> bool:
        """
        Full pipeline for one country:
          chunk → embed → index → save → smoke-test
        Returns True on success.
        """
        cfg = COUNTRY_CONFIG.get(country_code)
        if not cfg:
            logger.error(f"[ERROR] Unknown country code: {country_code}")
            return False

        data_dir = get_data_dir(country_code)
        vectorstore_path = get_vectorstore_path(country_code)
        display_name = cfg["display_name"]

        logger.info(f"\n{'='*70}")
        logger.info(f"[START] Building vector store for: {display_name}")
        logger.info(f"  Data dir      : {data_dir}")
        logger.info(f"  Vectorstore   : {vectorstore_path}")
        logger.info(f"{'='*70}")

        # 1 — Check data exists
        if not os.path.exists(data_dir) or not any(Path(data_dir).iterdir()):
            logger.warning(
                f"[SKIP] No policy documents found for {display_name} at {data_dir}. "
                "Add policy files and re-run."
            )
            return False

        # 2 — Chunk
        logger.info("[STEP 1] Chunking documents...")
        chunker = VisaDocumentChunker(data_path=data_dir)
        chunks = chunker.process_all()
        if not chunks:
            logger.error(f"[ERROR] No chunks produced for {display_name}. Skipping.")
            return False
        logger.info(f"[OK] {len(chunks)} chunks created.")

        # 3 — Embed
        logger.info("[STEP 2] Creating embeddings...")
        embeddings = self.create_embeddings(chunks)

        # 4 — Index
        logger.info("[STEP 3] Building FAISS index...")
        index = self.build_faiss_index(embeddings)

        # 5 — Save
        logger.info("[STEP 4] Saving vector store...")
        visa_counts: Dict[str, int] = {}
        for c in chunks:
            vtype = c.metadata.get("visa_type", "unknown")
            visa_counts[vtype] = visa_counts.get(vtype, 0) + 1

        self.save_vectorstore(
            index,
            chunks,
            vectorstore_path,
            metadata={
                "country": country_code,
                "display_name": display_name,
                "visa_types": list(visa_counts.keys()),
                "chunks_per_visa": visa_counts,
                "source_docs": len(
                    {c.metadata.get("source_file", "") for c in chunks}
                ),
            },
        )

        # 6 — Smoke test
        logger.info("[STEP 5] Running smoke-test queries...")
        chunks_meta = [
            {"id": i, "content": c.page_content, "metadata": c.metadata}
            for i, c in enumerate(chunks)
        ]
        test_queries = [
            "What are the financial requirements?",
            "What documents are needed to apply?",
            "What is the maximum allowed stay?",
        ]
        for q in test_queries:
            self.test_search(index, chunks_meta, q, k=2)

        logger.info(f"[DONE] {display_name} vector store built successfully.")
        logger.info(
            f"  Chunks: {len(chunks)} | Vectors: {index.ntotal} | "
            f"Dim: {self.embedding_dim}"
        )
        return True

    def build_all_countries(self, countries: Optional[List[str]] = None):
        """Build indexes for all (or a subset of) supported countries."""
        targets = countries or list(COUNTRY_CONFIG.keys())
        results: Dict[str, bool] = {}

        for code in targets:
            results[code] = self.build_for_country(code)

        # Summary
        logger.info("\n" + "=" * 70)
        logger.info("[SUMMARY] Build results:")
        for code, ok in results.items():
            status = "✓ SUCCESS" if ok else "✗ SKIPPED/FAILED"
            name = COUNTRY_CONFIG.get(code, {}).get("display_name", code)
            logger.info(f"  {status:16s} {name}")
        logger.info("=" * 70)
        return results


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="SwiftVisa — build FAISS vector stores for visa policy documents"
    )
    parser.add_argument(
        "--country",
        type=str,
        default=None,
        help="Country code to build (uk | canada | australia | new_zealand). "
             "Omit to build all countries.",
    )
    args = parser.parse_args()

    builder = VectorStoreBuilder(
        model_name="all-MiniLM-L6-v2",
        model_cache_dir="models/sentence_transformer",
    )

    if args.country:
        builder.build_for_country(args.country)
    else:
        builder.build_all_countries()


if __name__ == "__main__":
    main()