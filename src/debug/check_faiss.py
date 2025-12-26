from src.vector_store.faiss_store import FaissStore
from src.embeddings.embedder import Embedder

# Инициализация
store = FaissStore(dim=768, index_dir="data/faiss")
embedder = Embedder()

# Ваш текстовый запрос
query_text = "пример запроса"

# Получаем эмбеддинг
query_embedding = embedder.embed([query_text])[0]  # вернется list/np.array

# Поиск
results = store.search(query_embedding, top_k=5)

for r in results:
    print(r['text'])
    print("-"*50)

