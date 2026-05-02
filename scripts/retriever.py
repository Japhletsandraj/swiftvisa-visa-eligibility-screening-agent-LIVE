"""
SwiftVisa - RAG Retriever System
Retrieves relevant visa policy chunks from FAISS vector store
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
import pickle
import numpy as np
import faiss
from typing import List, Dict, Optional, Tuple
from sentence_transformers import SentenceTransformer

from config.config import (
    EMBEDDING_CONFIG,
    FAISS_CONFIG,
    RETRIEVAL_CONFIG,
    LOGGING_CONFIG
)

logging.basicConfig(level=LOGGING_CONFIG["level"], format=LOGGING_CONFIG["format"])
logger = logging.getLogger(__name__)


class VisaPolicyRetriever:
    """Retrieves relevant visa policy chunks using FAISS."""

    def __init__(
        self,
        vectorstore_path: str = None,   # PRIMARY arg — used by rag_pipeline.py
        index_path: str = None,          # legacy alias
        embedding_model_name: str = None,
        top_k: int = None,
    ):
        """
        Args:
            vectorstore_path: Path to the country-specific FAISS index directory.
                              Passed by SwiftVisaRAG for each country.
            index_path:       Deprecated alias for vectorstore_path.
            embedding_model_name: Sentence-transformer model name.
            top_k:            Default number of chunks to retrieve.
        """
        # Accept both argument names; vectorstore_path takes priority
        resolved_path = (
            vectorstore_path
            or index_path
            or FAISS_CONFIG["index_paths"].get("uk")   # safe fallback
        )
        self.index_path = resolved_path
        self.embedding_model_name = embedding_model_name or EMBEDDING_CONFIG["model_name"]
        self.top_k = top_k or RETRIEVAL_CONFIG["top_k"]

        logger.info(f"[RETRIEVER] Initialising — index: {self.index_path}")

        self.embedding_model = SentenceTransformer(
            self.embedding_model_name,
            cache_folder=EMBEDDING_CONFIG["cache_dir"],
        )
        self.index, self.chunks_metadata = self._load_vectorstore()
        logger.info("[RETRIEVER] Ready")

    # ── Vector store loading ──────────────────────────────────────────────────

    def _load_vectorstore(self) -> Tuple[faiss.Index, List[Dict]]:
        index_file = os.path.join(self.index_path, "index.faiss")
        chunks_file = os.path.join(self.index_path, "index.pkl")

        if not os.path.exists(index_file) or not os.path.exists(chunks_file):
            raise FileNotFoundError(
                f"Vector store not found at '{self.index_path}'. "
                "Run build_vectorstore.py for this country first."
            )

        index = faiss.read_index(index_file)
        logger.info(f"[FAISS] {index.ntotal} vectors loaded")

        with open(chunks_file, "rb") as f:
            chunks_metadata = pickle.load(f)
        logger.info(f"[CHUNKS] {len(chunks_metadata)} metadata entries loaded")

        return index, chunks_metadata

    # ── Embedding ─────────────────────────────────────────────────────────────

    def _create_query_embedding(self, query: str) -> np.ndarray:
        embedding = self.embedding_model.encode([query], convert_to_numpy=True)
        faiss.normalize_L2(embedding)
        return embedding

    # ── Core retrieval ────────────────────────────────────────────────────────

    def retrieve(
        self,
        query: str,
        top_k: int = None,
        visa_type_filter: Optional[str] = None,
        country_filter: Optional[str] = None,
        score_threshold: float = None,
    ) -> List[Dict]:
        """
        Retrieve relevant chunks for a query.

        Returns a flat list of chunk dicts — each has keys:
          content, metadata, score, chunk_id
        """
        k = top_k or self.top_k
        threshold = score_threshold or RETRIEVAL_CONFIG["score_threshold"]

        query_embedding = self._create_query_embedding(query)

        # Over-fetch if filtering so we have enough after applying filters
        search_k = k * 3 if (visa_type_filter or country_filter) else k
        distances, indices = self.index.search(query_embedding, search_k)

        results = []
        for idx, score in zip(indices[0], distances[0]):
            if score < threshold:
                continue

            chunk = self.chunks_metadata[idx]

            if visa_type_filter:
                if chunk["metadata"].get("visa_type", "") != visa_type_filter:
                    continue

            if country_filter:
                chunk_country = chunk["metadata"].get("country", "").lower()
                if chunk_country != country_filter.lower():
                    continue

            results.append({
                "content":  chunk["content"],
                "metadata": chunk["metadata"],
                "score":    float(score),
                "chunk_id": chunk["id"],
            })

            if len(results) >= k:
                break

        logger.info(f"[RETRIEVE] {len(results)} chunks for: '{query}'")
        return results

    def retrieve_with_context(
        self,
        query: str,
        user_context: Optional[Dict] = None,
        top_k: int = None,
    ) -> List[Dict]:
        """
        Retrieve chunks, using user_context to derive filters.

        Returns a FLAT LIST of chunk dicts (same as retrieve) so that
        rag_pipeline.py can iterate over results directly.
        """
        visa_type_filter = None
        country_filter = None

        if user_context:
            visa_type_filter = user_context.get("visa_type")
            # country is stored as the country_code string by rag_pipeline
            country_filter = (
                user_context.get("country")
                or user_context.get("Destination Country")
                or user_context.get("destination_country")
            )

        return self.retrieve(
            query=query,
            top_k=top_k,
            visa_type_filter=visa_type_filter,
            country_filter=country_filter,
        )

    # ── LLM context formatter ─────────────────────────────────────────────────

    def format_context_for_llm(
        self,
        retrieved_chunks: List[Dict],
        max_chars: int = None,
    ) -> str:
        """Format a flat list of retrieved chunks into a single context string."""
        max_chars = max_chars or RETRIEVAL_CONFIG["max_context_chars"]

        if not retrieved_chunks:
            return "No relevant policy information found."

        parts = []
        total = 0

        for i, chunk in enumerate(retrieved_chunks, 1):
            visa_label = chunk["metadata"].get("visa_type", "unknown").replace("_", " ").title()
            source = chunk["metadata"].get("source_file", "unknown")
            entry = (
                f"[Source {i}] {visa_label} — {source} "
                f"(Relevance: {chunk['score']:.3f})\n{chunk['content']}\n"
            )

            if total + len(entry) > max_chars and parts:
                logger.warning(f"[CONTEXT] Truncated at {total} chars")
                break

            parts.append(entry)
            total += len(entry)

        return "\n".join(parts)

    # ── Stats ─────────────────────────────────────────────────────────────────

    def get_statistics(self) -> Dict:
        visa_counts: Dict[str, int] = {}
        country_counts: Dict[str, int] = {}

        for chunk in self.chunks_metadata:
            vt = chunk["metadata"].get("visa_type", "unknown")
            co = chunk["metadata"].get("country", "unknown")
            visa_counts[vt] = visa_counts.get(vt, 0) + 1
            country_counts[co] = country_counts.get(co, 0) + 1

        return {
            "total_chunks":    len(self.chunks_metadata),
            "total_vectors":   self.index.ntotal,
            "visa_types":      visa_counts,
            "countries":       country_counts,
            "embedding_model": self.embedding_model_name,
            "index_path":      self.index_path,
            "top_k":           self.top_k,
        }


# ── CLI test ──────────────────────────────────────────────────────────────────

def test_retriever():
    import sys
    from utils.Country_config import COUNTRY_CONFIG
    from config.config import FAISS_CONFIG

    print("\n" + "=" * 70)
    print(" SwiftVisa — VisaPolicyRetriever test")
    print("=" * 70)

    # Pick country from CLI arg or default to uk
    country = sys.argv[1] if len(sys.argv) > 1 else "uk"
    index_path = FAISS_CONFIG["index_paths"].get(country)
    if not index_path:
        print(f"Unknown country '{country}'"); return

    print(f"\nCountry : {COUNTRY_CONFIG[country]['display_name']}")
    print(f"Index   : {index_path}\n")

    retriever = VisaPolicyRetriever(vectorstore_path=index_path)
    stats = retriever.get_statistics()
    print(f"Chunks  : {stats['total_chunks']}")
    print(f"Vectors : {stats['total_vectors']}")

    test_queries = [
        ("What are the financial requirements?", None),
        ("What documents are needed to apply?", None),
    ]

    for query, vfilter in test_queries:
        print(f"\n{'='*70}")
        print(f"Query  : {query}")
        results = retriever.retrieve(query=query, visa_type_filter=vfilter, top_k=3)
        for i, r in enumerate(results, 1):
            print(f"\n  [{i}] score={r['score']:.4f}  visa={r['metadata'].get('visa_type','?')}")
            print(f"      {r['content'][:200]}…")

        print("\n--- Formatted context ---")
        print(retriever.format_context_for_llm(results)[:400] + "…")


if __name__ == "__main__":
    test_retriever()