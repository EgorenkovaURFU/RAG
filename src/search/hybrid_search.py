from collections import defaultdict
from src.search.normalize import normalize_results
from loguru import logger
from config.config import Config


config = Config()


def hybrid_search(
    query: str,
    query_embedding,
    faiss_store,
    bm25_store,
    top_k: int = config.retrieval['top_k'],
    alpha: float = config.retrieval['hybrid_alpha'],
    debug: bool = config.retrieval['debug']
):
    faiss_results = faiss_store.search(
        query_embedding=query_embedding,
        top_k=top_k * 2,
    )

    bm25_results = bm25_store.search(
        query=query,
        top_k=top_k * 2,
    )

    if debug:
        logger.debug(f"[HYBRID] FAISS raw results: {len(faiss_results)}")
        logger.debug(f"[HYBRID] BM25  raw results: {len(bm25_results)}")

    faiss_results = normalize_results(faiss_results, source="faiss")
    bm25_results = normalize_results(bm25_results, source="bm25")

    combined = defaultdict(lambda: {
        "faiss": 0.0,
        "bm25": 0.0,
        "score": 0.0,
        "text": None,
        "metadata": None,
    })

    for r in faiss_results:
        key = r["metadata"]["chunk_id"]
        combined[key]["faiss"] = r["norm_score"]
        combined[key]["text"] = r["text"]
        combined[key]["metadata"] = r["metadata"]

    for r in bm25_results:
        key = r["metadata"]["chunk_id"]
        combined[key]["bm25"] = r["norm_score"]
        combined[key]["text"] = r["text"]
        combined[key]["metadata"] = r["metadata"]

    results = []

    for chunk_id, data in combined.items():
        final_score = alpha * data["faiss"] + (1 - alpha) * data["bm25"]
        data["score"] = final_score

        if debug:
            logger.debug(
                f"[HYBRID] chunk={chunk_id} | "
                f"faiss={data['faiss']:.3f} | "
                f"bm25={data['bm25']:.3f} | "
                f"final={final_score:.3f}"
            )

        results.append({
            "id": data["metadata"].get("id"),
            "score": final_score,
            "text": data["text"],
            "metadata": data["metadata"],
        })

    results.sort(key=lambda x: x["score"], reverse=True)

    return results[:top_k]