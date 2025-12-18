from loguru import logger
from legacy.chroma_store import ChromaStore


def debug_chroma(limit=5):
    store = ChromaStore()

    logger.info("Trying to read from ChromaDB...")

    data = store.collection.get(
        include=["documents", "metadatas"],
        limit=limit
    )

    docs = data.get("documents", [])
    metas = data.get("metadatas", [])

    if not docs:
        logger.warning("ChromaDB is EMPTY")
        return

    logger.success(f"ChromaDB contains at least {len(docs)} documents")

    for i, (doc, meta) in enumerate(zip(docs, metas)):
        print("\n" + "=" * 80)
        print(f"DOC #{i}")
        print("TEXT SAMPLE:")
        print(doc[:300])
        print("METADATA:")
        print(meta)


if __name__ == "__main__":
    debug_chroma()

    