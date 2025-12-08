import chromadb
from chromadb.config import Settings
from loguru import logger


class ChromaStore:

    def __init__(self, path='rag/db'):
        logger.info(f'Init ChromaDB in {path}')

        self.client = chromadb.PersistentClient(path)
        self.collection = self.client.get_or_create_collection(
            name='documents',
            metadata={"hnsw:space": "cosine"}
        )

    def add(self, ids, embeddings, documents, metadatas):
        """
        Add chunks in ChromaDB
        
        :param self: Description
        :param ids: Description
        :param embeddings: Description
        :param documents: Description
        :param metadatas: Description
        """
        logger.info(f'Adding {len(ids)} documents in ChromaDB')

        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )

    def query(self, query_embeddings, n=3):
        """
        Search similar documents.
        
        :param self: Description
        :param query_embeddings: Description
        :param n: Description
        """

        logger.info(f'Searching into the database')

        result = self.collection.query(
            query_embeddings=[query_embeddings],
            n_results=n
        )
        return result

