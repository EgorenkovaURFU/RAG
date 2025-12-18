from vector_store.chroma_store import ChromaStore

store = ChromaStore()
data = store.collection.get(include=['documents', 'metadatas'])

docs = data['documents']
metas = data['metadatas']

# В некоторых версиях ChromaDB docs/metas — это список списков
if docs and isinstance(docs[0], list):
    docs = docs[0]
    metas = metas[0]

print(f"Documents: {len(docs)}, Metadatas: {len(metas)}")

# При желании можно распечатать первые несколько метаданных
for i, meta in enumerate(metas[:5]):
    print(i, meta)