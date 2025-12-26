# src/chunking/bm25_chunker.py

import re
from typing import List, Dict
from loguru import logger


# -----------------------------
# Очистка текста под BM25
# -----------------------------

_PUNCT_RE = re.compile(r"[^\w\s]")


def clean_text_for_bm25(text: str) -> str:
    """
    Агрессивная очистка текста под BM25
    """
    text = text.lower()
    text = _PUNCT_RE.sub(" ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# -----------------------------
# Разбиение на предложения
# -----------------------------

_SENTENCE_SPLIT_RE = re.compile(
    r"(?<=[.!?])\s+"
)


def split_into_sentences(text: str) -> List[str]:
    """
    Простое и предсказуемое разбиение на предложения
    (без NLP-магии, зато стабильно)
    """
    sentences = _SENTENCE_SPLIT_RE.split(text)
    return [s.strip() for s in sentences if s.strip()]


# -----------------------------
# Основной chunker
# -----------------------------

def chunk_document_for_bm25(
    pages: List[Dict],
    min_chars: int = 40,
    max_chars: int = 500,
) -> List[Dict]:
    """
    Делает sentence-level чанки для BM25
    """

    chunks = []
    chunk_id = 0

    for page in pages:
        raw_text = page.get("text", "")
        if not raw_text or len(raw_text.strip()) < min_chars:
            continue

        sentences = split_into_sentences(raw_text)

        buffer = ""
        buffer_sent_ids = []

        for sent_idx, sentence in enumerate(sentences):

            if not sentence.strip():
                continue

            # Накопление коротких предложений
            if len(sentence) < min_chars:
                buffer += " " + sentence
                buffer_sent_ids.append(sent_idx)
                continue

            # Если в буфере что-то есть — сначала сбрасываем его
            if buffer:
                cleaned = clean_text_for_bm25(buffer)
                if len(cleaned) >= min_chars:
                    chunks.append(_make_chunk(
                        page, cleaned, chunk_id, buffer_sent_ids
                    ))
                    chunk_id += 1
                buffer = ""
                buffer_sent_ids = []

            # Основное предложение
            cleaned = clean_text_for_bm25(sentence)
            if min_chars <= len(cleaned) <= max_chars:
                chunks.append(_make_chunk(
                    page, cleaned, chunk_id, [sent_idx]
                ))
                chunk_id += 1

        # Хвост
        if buffer:
            cleaned = clean_text_for_bm25(buffer)
            if len(cleaned) >= min_chars:
                chunks.append(_make_chunk(
                    page, cleaned, chunk_id, buffer_sent_ids
                ))
                chunk_id += 1

    logger.info(f"[BM25] created {len(chunks)} sentence-level chunks")
    return chunks


def _make_chunk(page, text, chunk_id, sent_ids):
    """
    Унифицированная структура чанка
    """
    return {
        "text": text,
        "chunk_id": chunk_id,

        # навигация
        "doc_id": page.get("doc_id"),
        "path": page.get("path"),
        "file_type": page.get("file_type"),
        "page": page.get("page"),
        "sheet": page.get("sheet"),
        "section": page.get("section"),

        # важно для восстановления контекста
        "sentence_ids": sent_ids,
        "type": "bm25_sentence",
    }
