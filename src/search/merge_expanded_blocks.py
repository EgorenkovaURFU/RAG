from typing import List, Dict, Any


def merge_expanded_blocks(
    expanded_blocks: List[Dict[str, Any]],
    *,
    max_chars: int = 4000,
    max_chunk_gap: int = 1,
) -> List[Dict[str, Any]]:
    """
    Объединяет expanded BM25-блоки, если они относятся к одному документу
    и имеют соседние chunk_indices.

    Parameters
    ----------
    expanded_blocks : list of dict
        Результат expand_bm25_context()
    max_chars : int
        Максимальный размер объединённого текста
    max_chunk_gap : int
        Максимально допустимый разрыв между чанками для склейки

    Returns
    -------
    list of dict
        Объединённые блоки
    """

    if not expanded_blocks:
        return []

    # 1. сортируем по документу и позиции
    blocks = sorted(
        expanded_blocks,
        key=lambda b: (
            b["path"],
            min(b["chunk_indices"]),
        )
    )

    merged = []
    current = None

    for block in blocks:
        if current is None:
            current = dict(block)
            current["chunk_indices"] = list(block["chunk_indices"])
            continue

        # Проверяем, можно ли склеить
        same_doc = block["path"] == current["path"]

        prev_max = max(current["chunk_indices"])
        next_min = min(block["chunk_indices"])

        close_enough = next_min - prev_max <= max_chunk_gap

        size_ok = len(current["text"]) + len(block["text"]) <= max_chars

        if same_doc and close_enough and size_ok:
            # 🔹 склеиваем
            current["text"] += "\n" + block["text"]
            current["chunk_indices"].extend(block["chunk_indices"])
            current["chunk_indices"] = sorted(set(current["chunk_indices"]))

            # якорный bm25 — лучший
            current["bm25_score"] = max(
                current["bm25_score"],
                block["bm25_score"]
            )

            # страницу оставляем минимальную (обычно начало секции)
            if current.get("page") is not None and block.get("page") is not None:
                current["page"] = min(current["page"], block["page"])

        else:
            merged.append(current)
            current = dict(block)
            current["chunk_indices"] = list(block["chunk_indices"])

    if current:
        merged.append(current)

    return merged
