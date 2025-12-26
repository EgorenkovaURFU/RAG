from src.vector_store.bm25_store import BM25Store

bm25 = BM25Store()
bm25.load()  # подгружает данные из файла, указанного в BM25Store.path

query = "пример запроса"
results = bm25.search(query, top_k=5)

print(results)

