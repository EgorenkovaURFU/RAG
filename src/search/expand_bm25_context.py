from typing import List, Dict, Any


def expand_bm25_context(
    bm25_hits: List[Dict[str, Any]],
    all_chunks: List[Dict[str, Any]],
    *,
    window_before: int = 3,
    window_after: int = 10,
    max_chars: int = 2500,
) -> List[Dict[str, Any]]:
    """
    Расширяет BM25-чанки соседним контекстом (внутри одного документа).
    """

    expanded_blocks = []

    for hit in bm25_hits:
        meta = hit["metadata"]

        anchor_chunk_id = meta["chunk_id"]
        doc_id = meta["doc_id"]
        path = meta["path"]
        page = meta.get("page")

        # 1️⃣ Берём ТОЛЬКО чанки этого документа
        doc_chunks = [
            c for c in all_chunks
            if c["metadata"]["doc_id"] == doc_id
        ]

        if not doc_chunks:
            continue

        # 2️⃣ Сортируем их в естественном порядке документа
        doc_chunks.sort(
            key=lambda c: (
                c["metadata"].get("page", 0),
                c["metadata"].get("chunk_id", 0),
            )
        )

        # 3️⃣ Находим позицию якоря
        anchor_pos = None
        for i, c in enumerate(doc_chunks):
            if c["metadata"]["chunk_id"] == anchor_chunk_id:
                anchor_pos = i
                break

        if anchor_pos is None:
            continue

        # 4️⃣ Берём окно вокруг якоря
        start = max(0, anchor_pos - window_before)
        end = min(len(doc_chunks), anchor_pos + window_after + 1)

        collected_chunks = []
        current_length = 0

        for c in doc_chunks[start:end]:
            text = c["text"].strip()
            if not text:
                continue

            if current_length + len(text) > max_chars:
                break

            collected_chunks.append(c)
            current_length += len(text)

        if not collected_chunks:
            continue

        merged_text = "\n".join(c["text"] for c in collected_chunks)

        expanded_blocks.append({
            "text": merged_text,
            "metadata": collected_chunks[0]["metadata"],
            "anchor_chunk_id": anchor_chunk_id,
            "bm25_score": hit["score"],
            "path": path,
            "page": page,
            "chunk_indices": [
                c["metadata"]["chunk_id"] for c in collected_chunks
            ],
        })

    return expanded_blocks
