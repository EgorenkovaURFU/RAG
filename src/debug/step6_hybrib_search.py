from loguru import logger

from src.embeddings.embedder import Embedder
from src.vector_store.faiss_store import FaissStore
from src.vector_store.bm25_store import BM25Store
import sys

logger.remove()  # удаляем стандартный handler
logger.add(
    sys.stderr,
    level="DEBUG",
    format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}"
)


QUERY = "проверка наличия трансмиссионной связи валов"


def normalize(results):
    if not results:
        return {}

    max_score = max(r["score"] for r in results)
    return {
        r["metadata"]["chunk_id"]: {
            **r,
            "score": r["score"] / max_score if max_score > 0 else 0.0
        }
        for r in results
    }


if __name__ == "__main__":
    logger.info("HYBRID SEARCH DEBUG")

    embedder = Embedder()
    faiss_store = FaissStore(dim=384)
    bm25_store = BM25Store()
    bm25_store.load()

    # ---------- FAISS ----------
    logger.info("FAISS search")
    query_emb = embedder.embed([QUERY])[0]

    faiss_results = faiss_store.search(
        query_embedding=query_emb,
        top_k=5
    )

    # ---------- BM25 ----------
    logger.info("BM25 search")
    bm25_results = bm25_store.search(
        query=QUERY,
        top_k=5
    )

    # ---------- NORMALIZE ----------
    faiss_norm = normalize(faiss_results)
    bm25_norm = normalize(bm25_results)

    # ---------- FUSION ----------
    hybrid = {}

    for key, r in faiss_norm.items():
        hybrid[key] = {
            **r,
            "score": r["score"] * 0.6
        }

    for key, r in bm25_norm.items():
        if key in hybrid:
            hybrid[key]["score"] += r["score"] * 0.4
        else:
            hybrid[key] = {
                **r,
                "score": r["score"] * 0.4
            }

    # ---------- SORT ----------
    ranked = sorted(
        hybrid.values(),
        key=lambda x: x["score"],
        reverse=True
    )

    # ---------- OUTPUT ----------
    print("\n" + "=" * 80)
    print("HYBRID SEARCH RESULTS")
    print("=" * 80)

    for r in ranked:
        print(f"SCORE: {r['score']:.4f}")
        print(f"PAGE: {r['metadata']['page']}")
        print(r["text"][:200])
        print("-" * 80)
