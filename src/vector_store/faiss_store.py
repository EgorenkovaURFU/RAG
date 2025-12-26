from pathlib import Path
import pickle
from typing import List, Dict

import faiss
import numpy as np
from loguru import logger


class FaissStore:
    def __init__(self, dim: int, index_dir="data/faiss", normalize=True):
        self.dim = dim
        self.normalize = normalize

        self.index_dir = Path(index_dir)
        self.index_file = self.index_dir / "index.faiss"
        self.meta_file = self.index_dir / "meta.pkl"

        self.index = None
        self.ids: List[str] = []
        self.texts: List[str] = []
        self.metadatas: List[Dict] = []

        self.index_dir.mkdir(parents=True, exist_ok=True)

        if self.index_file.exists() and self.meta_file.exists():
            self._load()
        else:
            self._create_new()

    def _create_new(self):
        logger.info("Creating new FAISS index")
        self.index = faiss.IndexFlatIP(self.dim)

    def _load(self):
        logger.info("Loading FAISS index from disk")

        self.index = faiss.read_index(str(self.index_file))

        with open(self.meta_file, "rb") as f:
            data = pickle.load(f)

        self.ids = data["ids"]
        self.texts = data["texts"]
        self.metadatas = data["metadatas"]

        assert self.index.ntotal == len(self.ids)

        logger.success(f"FAISS loaded: {self.index.ntotal} vectors")

    def _normalize(self, x: np.ndarray):
        if not self.normalize:
            return x
        return x / (np.linalg.norm(x, axis=1, keepdims=True) + 1e-10)

    def add(self, ids, embeddings, texts, metadatas):
        assert len(ids) == len(texts) == len(metadatas)

        embeddings = np.array(embeddings, dtype="float32")
        embeddings = self._normalize(embeddings)

        self.index.add(embeddings)

        self.ids.extend(ids)
        self.texts.extend(texts)
        self.metadatas.extend(metadatas)

        logger.info(f"Added {len(ids)} vectors (total={self.index.ntotal})")

    def search(self, query_embedding, top_k=5):
        if self.index.ntotal == 0:
            return []

        q = np.array(query_embedding, dtype="float32").reshape(1, -1)
        q = self._normalize(q)

        scores, indices = self.index.search(q, top_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
           
            meta = self.metadatas[idx]

            results.append({
                "id": meta["chunk_id"],          # 🔑 ВСЕГДА id
                "score": float(score),
                "norm_score": 0.0,         # заполним позже
                "source": "faiss",
                "text": self.texts[idx],
                "metadata": meta})

        return results

    def save(self):
        faiss.write_index(self.index, str(self.index_file))
        with open(self.meta_file, "wb") as f:
            pickle.dump({
                "ids": self.ids,
                "texts": self.texts,
                "metadatas": self.metadatas,
            }, f)

        logger.success(f"FAISS saved: {self.index.ntotal}")
