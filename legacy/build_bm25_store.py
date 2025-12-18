from loguru import logger
from legacy.chroma_store import ChromaStore
from src.vector_store.bm25_store import BM25Store
import os


BM25_PATH = 'data/bm25_index.pkl'


def export_all_chunks(store: ChromaStore):
    """
    Get all documents and metedata from Chroma
    
    :param store: Store with data
    :type store: ChromaStore
    """

    data = store.collection.get(include=['documents', 'metadatas'])

    logger.info('----------get data-----------')

    docs = data['documents']
    metas = data['metadatas']

    if docs and isinstance(docs[0], list):
        docs = docs[0]
        metas = metas[0]
    
    return docs, metas


def build_bm25_store():
    logger.info('Load data from ChromaDB')

    store = ChromaStore()
    docs, metas = export_all_chunks(store)

    logger.info(f'Got {len(docs)} chunks from Chroma')

    if not docs:
        logger.warning("No documents found in ChromaDB — BM25 will not be built")
        return

    bm25 = BM25Store()
    bm25.add(docs, metas)

    
    os.makedirs("data", exist_ok=True)
    bm25.save(BM25_PATH)

    logger.info(f"BM25 index saved to {BM25_PATH}")


if __name__ == '__main__':
    build_bm25_store()

