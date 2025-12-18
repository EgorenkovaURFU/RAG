from sentence_transformers import CrossEncoder


class Reranker:

    def __init__(self, model_name='cross-encoder/ms-marco-MiniLM-L6-v2'):
        self.model = CrossEncoder(model_name)

    def rerank(self, query: str, docs: list, top_k: int = 3):
        """
        Return top_k relevant documents 
        
        :param query: query from users.
        :type query: str
        :param docs: List of strings.
        :type docs: list
        :param top_k: Number of top documents
        :type top_k: int
        """

        if not docs:
            return []
        
        pairs = [(query, d) for d in docs]

        scores = self.model.predict(pairs)

        ranked = sorted(zip(docs, scores), key=lambda x: x[1], reverse=True)

        return [doc for doc, score in ranked[:top_k]]
    
