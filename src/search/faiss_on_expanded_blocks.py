from typing import List, Dict, Any
import numpy as np
import faiss


def faiss_select_from_blocks(
    query_embedding: np.ndarray,
    blocks: List[Dict[str, Any]],
    block_embeddings: np.ndarray,
    *,
    top_k: int = 3,
) -> List[Dict[str, Any]]:
    """
    Выбирает лучшие блоки с помощью FAISS
    ТОЛЬКО из расширенных BM25-контекстов.

    Parameters
    ----------
    query_embedding : np.ndarray
        Вектор запроса (shape: [dim])
    blocks : list of dict
        Результат merge_expanded_blocks()
    block_embeddings : np.ndarray
        Эмбеддинги блоков (shape: [N, dim])
    top_k : int
        Сколько блоков вернуть

    Returns
    -------
    list of dict
        Отсортированные блоки с dense_score
    """

    if not blocks:
        return []

    dim = block_embeddings.shape[1]

    # 🔹 создаём временный FAISS индекс
    index = faiss.IndexFlatIP(dim)
    index.add(block_embeddings)

    # 🔹 поиск
    scores, indices = index.search(
        query_embedding.reshape(1, -1),
        min(top_k, len(blocks))
    )

    results = []
    for score, idx in zip(scores[0], indices[0]):
        block = dict(blocks[idx])
        block["faiss_score"] = float(score)
        results.append(block)

    # на всякий случай сортируем
    results.sort(key=lambda b: b["faiss_score"], reverse=True)

    return results

