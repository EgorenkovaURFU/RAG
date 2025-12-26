import re
import pickle
from rank_bm25 import BM25Okapi
from loguru import logger
from config.config import Config


config = Config()


STOPWORDS = {
    "и", "в", "на", "для", "по", "с", "к", "от", "из",
    "что", "это", "как", "так", "же", "или"
}


def bm25_tokenize(text: str):
    text = text.lower()
    text = re.sub(r"[^а-яa-z0-9\s]", " ", text)
    tokens = text.split()
    return [t for t in tokens if t not in STOPWORDS and len(t) > 2]


class BM25Store:
    def __init__(self):
        logger.info("Creating BM25 store")
        self.documents = []   # [{text, metadata}]
        self.bm25 = None

    def iter_documents(self):
        return iter(self.documents)

    def add(self, texts: list[str], metadatas: list[dict]):
        assert len(texts) == len(metadatas)

        logger.info(f"Adding {len(texts)} documents to BM25")

        for text, meta in zip(texts, metadatas):
            self.documents.append({
                "text": text,
                "metadata": meta
            })

        tokenized = [bm25_tokenize(d["text"]) for d in self.documents]
        self.bm25 = BM25Okapi(tokenized)

        logger.success("BM25 index built")

    def search(self, query: str, top_k: int = 5):
        if self.bm25 is None:
            logger.warning("BM25 index not built")
            return []

        scores = self.bm25.get_scores(bm25_tokenize(query))

        ranked = sorted(
            enumerate(scores),
            key=lambda x: x[1],
            reverse=True
        )[:top_k]

        results = []
        for idx, score in ranked:
            if score <= 0:
                continue

            doc = self.documents[idx]

            results.append({
                "id": doc["metadata"]["chunk_id"],
                "score": float(score),
                "norm_score": 0.0,
                "source": "bm25",
                "text": doc["text"],
                "metadata": doc["metadata"]})

        return results

    def save(self, path=config.paths["bm25_index"]):
        with open(path, "wb") as f:
            pickle.dump(self.documents, f)
        logger.success(f"BM25 saved to {path}")

    def load(self, path=config.paths["bm25_index"]):
        with open(path, "rb") as f:
            self.documents = pickle.load(f)

        tokenized = [bm25_tokenize(d["text"]) for d in self.documents]
        self.bm25 = BM25Okapi(tokenized)

        logger.success(f"BM25 loaded from {path}")
        return self
