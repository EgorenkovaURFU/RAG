from loguru import logger

from src.embeddings.embedder import Embedder
from src.vector_store.faiss_store import FaissStore


def main():
    logger.info("Loading embedder")
    embedder = Embedder()

    logger.info("Loading FAISS store")
    store = FaissStore(dim=384)

    queries = [
        "Область применения",
        "Технологическая инструкция по проверке трансмиссии УЭЦН",
        "Экологические аспекты производства",
    ]

    for query in queries:
        logger.info(f"\n🔍 QUERY: {query}")

        query_embedding = embedder.embed([query])[0]

        results = store.search(
            query_embedding=query_embedding,
            top_k=5
        )

        if not results:
            logger.warning("No results")
            continue

        for i, r in enumerate(results, 1):
            print(
                f"\n#{i}"
                f"\nScore: {r['score']:.4f}"
                f"\nPage: {r['metadata'].get('page')}"
                f"\nPath: {r['metadata'].get('path')}"
                f"\nText:\n{r['text'][:500]}"
            )


if __name__ == "__main__":
    main()
