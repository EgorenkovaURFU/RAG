from sentence_transformers import CrossEncoder


class Reranker:

    def __init__(self, model_name='cross-encoder/ms-marco-MiniLM-L6-v2'):
        self.model = CrossEncoder(model_name)

    def rerank(self, query: str, results: list[dict], top_k: int = 3) -> list[dict]:
        """
        Return top_k relevant documents 
        
        :param query: query from users.
        :type query: str
        :param docs: List of strings.
        :type docs: list
        :param top_k: Number of top documents
        :type top_k: int
        """

        if not results:
            return []
        
        texts = [r["text"] for r in results]
        pairs = [(query, t) for t in texts]

        scores = self.model.predict(pairs)

        for r, s in zip(results, scores):
            r["rerank_score"] = float(s)

        ranked = sorted(
            results,
            key=lambda x: x["rerank_score"],
            reverse=True
        )

        return ranked[:top_k]
    
