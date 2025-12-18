from src.embeddings.embedder import Embedder
from legacy.chroma_store import ChromaStore


query = 'Как заменить фильтр на установке?'
embedder = Embedder()
store = ChromaStore()

q_emb = embedder.embed(query)[0]
res = store.query(q_emb, n=3)

print('Search results:')
for doc, meta in zip(res['documents'][0], res['metadatas'][0]):
    print('--------------------')
    print(doc[:200], '...')
    print(meta)

