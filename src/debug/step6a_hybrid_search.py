# src/debug/step6_hybrid_search.py

import sys
from loguru import logger

from src.embeddings.embedder import Embedder
from src.vector_store.faiss_store import FaissStore
from src.vector_store.bm25_store import BM25Store
from src.search.hybrid_search import hybrid_search


# ---------------------------------------------------------------------
# Logger: DEBUG mode
# ---------------------------------------------------------------------
logger.remove()
logger.add(
    sys.stderr,
    level="DEBUG",
    format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}"
)

# ---------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------
QUERY = "проверка наличия трансмиссионной связи валов"
TOP_K = 5


# ---------------------------------------------------------------------
# Debug entry point
# ---------------------------------------------------------------------
if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info("HYBRID SEARCH DEBUG (via hybrid_search)")
    logger.info("=" * 80)

    # --- init ---
    embedder = Embedder()

    faiss_store = FaissStore(dim=384)
    bm25_store = BM25Store().load()

    # --- embed query ---
    query_embedding = embedder.embed([QUERY])[0]

    # --- run hybrid search ---
    logger.info("Running hybrid_search()")

    results = hybrid_search(
        query=QUERY,
        query_embedding=query_embedding,
        faiss_store=faiss_store,
        bm25_store=bm25_store,
        top_k=TOP_K,
        alpha=0.6
    )

    # -----------------------------------------------------------------
    # Output
    # -----------------------------------------------------------------
    print("\n" + "=" * 80)
    print("HYBRID SEARCH RESULTS")
    print("=" * 80)

    for i, r in enumerate(results, 1):
        meta = r.get("metadata", {})

        print(f"[{i}] SCORE: {r['score']:.4f}")
        print(f"    PAGE: {meta.get('page')}")
        print(f"    ID:   {meta.get('id')}")
        print(f"    TEXT: {r['text'][:200].strip()}")
        print("-" * 80)

    if not results:
        print("NO RESULTS RETURNED")
