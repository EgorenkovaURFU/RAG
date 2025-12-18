# import chromadb
# from chromadb.config import Settings
# from loguru import logger


# class ChromaStore:

#     def __init__(self, path='chroma/db'):
#         logger.info(f'Init ChromaDB in {path}')

#         self.client = chromadb.Client(
#             Settings(
#             persist_directory=path,
#             chroma_db_impl="duckdb+parquet"
#                 )
#             )
#         self.collection = self.client.get_or_create_collection(
#             name='documents',
#             metadata={"hnsw:space": "cosine"}
#         )

#     def add(self, ids, embeddings, documents, metadatas):
#         """
#         Add chunks in ChromaDB
        
#         :param self: Description
#         :param ids: Description
#         :param embeddings: Description
#         :param documents: Description
#         :param metadatas: Description
#         """
#         logger.info(f'Adding {len(ids)} documents in ChromaDB')

#         self.collection.add(
#             ids=ids,
#             embeddings=embeddings,
#             documents=documents,
#             metadatas=metadatas
#         )
#         self.client.persist()


#     def query(self, query_embeddings, n=3):
#         """
#         Search similar documents.
        
#         :param query_embeddings: user's query as embedding
#         :param n: number of relevant documents
#         """

#         logger.info(f'Searching into the database')

#         result = self.collection.query(
#             query_embeddings=[query_embeddings],
#             n_results=n
#         )
#         return result

# import chromadb
# from chromadb.config import Settings
# from loguru import logger


# import chromadb
# from loguru import logger

# class ChromaStore:
#     def __init__(self, path="chroma/db"):
#         logger.info(f"Init ChromaDB in {path}")

#         # Создаём клиент
#         self.client = chromadb.Client(path)

#         # Создаём коллекцию, указываем persist_directory через self.client.persist() позже
#         self.collection = self.client.create_collection(name="documents")

#     def add(self, ids, embeddings, documents, metadatas):
#         logger.info(f"Adding {len(ids)} documents in ChromaDB")
#         self.collection.add(
#             ids=ids,
#             embeddings=embeddings,
#             documents=documents,
#             metadatas=metadatas
#         )
#         # Для сохранения на диск нужно вызывать persist()
#         #self.client.persist("chroma/db")
#         logger.info(f"---------Added {len(ids)} documents in ChromaDB")

#     def query(self, query_embeddings, n=3):
#         logger.info("Searching into the database")
#         return self.collection.query(
#             query_embeddings=[query_embeddings],
#             n_results=n
#         )

import chromadb
from chromadb.utils import embedding_functions
from loguru import logger

class ChromaStore:
    """
    Обёртка для работы с ChromaDB с использованием кастомного Embedder.
    """

    def __init__(self, embedder, collection_name='documents', path='chroma/db'):
        """
        :param embedder: объект твоего Embedder, который имеет метод embed(list[str]) -> list[list[float]]
        :param collection_name: имя коллекции в базе
        :param path: путь для хранения данных ChromaDB
        """
        logger.info(f'Init ChromaDB in {path}')

        # Создаём клиент
        self.client = chromadb.PersistentClient(path)

        # Обёртываем Embedder в Chroma embedding_function
        self.embedding_function = embedding_functions.DefaultEmbeddingFunction(
            embedder=lambda texts: embedder.embed(texts)
        )

        # Получаем или создаём коллекцию с нашей функцией эмбеддингов
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_function
        )

    def add(self, ids, embeddings, documents, metadatas):
        """
        Добавление документов в ChromaDB
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
        Поиск похожих документов по embedding
        """
        logger.info(f'Searching in ChromaDB for top {n} results')

        result = self.collection.query(
            query_embeddings=[query_embeddings],
            n_results=n
        )
        return result

    def count(self):
        """
        Возвращает количество документов в коллекции
        """
        return self.collection.count()
