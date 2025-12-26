# import re
# from loguru import logger


# def filter_content_pages(pages: list) -> list:
#     content = [p for p in pages if p.get("page_type") == "content"]
#     logger.info(f"Content pages: {len(content)} / {len(pages)}")
#     return content


# def spllit_into_sentences(text: str) -> list:
#     """
#     Docstring for spllit_into_sentences
    
#     :param text: Description
#     :type text: str
#     :return: Description
#     :rtype: list
#     """
#     text = text.replace("\n", " ")
#     sentences = re.split(r"(?<=[.!?])\s+", text)
#     return [s.strip() for s in sentences if s.strip()]


# # def chunk_text(text: str, max_tokens: int = 500) -> list:
# #     """
# #     Docstring for chunk_text
    
# #     :param text: Description
# #     :type text: str
# #     :param max_tokens: Description
# #     :type max_tokens: int
# #     :return: Description
# #     :rtype: list
# #     """

# #     text = str(text)
# #     sentences = spllit_into_sentences(text)
# #     chunks = []

# #     current_chunk = []
# #     current_length = 0

# #     for sent in sentences:
# #         sent = str(sent)
# #         sent_len = len(sent.split())

# #         if current_length + sent_len < max_tokens:
# #             chunks.append(" ".join(current_chunk))
# #             current_chunk = [sent]
# #             current_length = sent_len
# #         else:
# #             current_chunk.append(sent)
# #             current_length += sent_len
    
# #     if current_chunk:
# #         chunks.append(" ".join(current_chunk))

# #     return chunks

# def split_into_paragraphs(text: str) -> list[str]:
#     """
#     Split text into meaningful paragraphs.
#     """
#     paragraphs = re.split(r"\n\s*\n", text)
#     return [p.strip() for p in paragraphs if len(p.strip()) > 30]


# def chunk_by_paragraphs(
#     text: str,
#     max_tokens: int = 500,
#     min_tokens: int = 150) -> list[str]:
#     """
#     Build large chunks from paragraphs.
#     """
#     paragraphs = split_into_paragraphs(text)

#     chunks = []
#     current = []
#     current_len = 0

#     for p in paragraphs:
#         p_len = len(p.split())

#         if current_len + p_len <= max_tokens:
#             current.append(p)
#             current_len += p_len
#         else:
#             if current_len >= min_tokens:
#                 chunks.append("\n".join(current))
#                 current = [p]
#                 current_len = p_len
#             else:
#                 # forcibly extend small chunk
#                 current.append(p)
#                 current_len += p_len

#     if current:
#         chunks.append("\n".join(current))

#     return chunks


# def chunk_text(text: str, max_tokens: int = 500) -> list:
#     text = str(text)
#     sentences = spllit_into_sentences(text)

#     chunks = []
#     current_chunk = []
#     current_length = 0

#     for sent in sentences:
#         sent_len = len(sent.split())

#         if current_length + sent_len <= max_tokens:
#             current_chunk.append(sent)
#             current_length += sent_len
#         else:
#             if current_chunk:
#                 chunks.append(" ".join(current_chunk))
#             current_chunk = [sent]
#             current_length = sent_len

#     if current_chunk:
#         chunks.append(" ".join(current_chunk))

#     return chunks


# def chunk_document_by_paragraphs(
#     pages: list,
#     max_tokens: int = 10,
# ):
#     results = []

#     for page in pages:
#         text = page.get("text", "").strip()
#         if not text:
#             continue

#         chunks = chunk_by_paragraphs(text, max_tokens=max_tokens)

#         for idx, chunk in enumerate(chunks):
#             results.append({
#                 "text": chunk,
#                 "chunk_id": idx,
#                 "page": page.get("page"),
#                 "path": page.get("path"),
#                 "file_type": page.get("file_type"),
#                 "sheet": page.get("sheet"),
#                 "section": page.get("section"),
#                 "type": page.get("page_type"),
#             })

#     return results



# def progress_document(parsed_pages: list, max_tokens=500) -> list:
#     """
#     Docstring for progress_document
    
#     :param parsed_pages: Description
#     :type parsed_pages: list
#     :param max_tokens: Description
#     :return: Description
#     :rtype: list
#     """
#     if not parsed_pages:
#         logger.warning("⚠️ Document skipped: no parsed pages")
#         return []
    
#     results = []
#     logger.info(
#         f"Starting chunking document: {parsed_pages[0].get('path', 'unknown')}"
#     )

#     for entry in parsed_pages:
#         text = entry.get("text", "").strip()
#         if not text:
#             continue

#         chunks = chunk_text(text, max_tokens=max_tokens)

#         for idx, chunk in enumerate(chunks):
#             results.append({
#                 "text": chunk,
#                 "chunk_id": idx,
#                 "page": entry.get("page"),
#                 "path": entry.get("path"),
#                 "type": entry.get("page_type"),
#                 "file_type": entry.get("file_type"),
#                 "sheet": entry.get("sheet"),
#                 "section": entry.get("section")
#             })

#     if not results:
#         logger.warning(
#             f"Document produced no chunks: {parsed_pages[0].get('path', 'unknown')}"
#         )

#     logger.info(f"Chanking was finished: got {len(results)} chunks")
#     return results


# class TextSplitter:
#     """
#     """

#     def __init__(self, chunk_size: int = 500, chunk_overlap: int = 0):
#         self.max_tokens = chunk_size
#         self.chunk_overlap = chunk_overlap

#     def split_text(self, text: str) -> list[str]:
#         return chunk_text(text, max_tokens=self.max_tokens)


# # Test
# if __name__ == "__main__":
#     sample = [
#         {
#             "text": "This is an example text. It will be divided into several sentences.",
#             "page": 1,
#             "path": "test.pdf",
#             "type": "pdf"
#         }
#     ]

#     res = progress_document(sample)
#     print(res)


import re
from loguru import logger
from typing import List, Dict


# =========================================================
# Helpers
# =========================================================

def normalize_text(text: str) -> str:
    text = text.replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


def split_into_paragraphs(text: str) -> List[str]:
    paragraphs = re.split(r"\n\s*\n", text)
    return [p.strip() for p in paragraphs if p.strip()]


# =========================================================
# Cleaning
# =========================================================

SECTION_ONLY_RE = re.compile(r"^[\d\W]{1,10}$")
TOO_MANY_ABBR_RE = re.compile(r"(?:\b[A-ZА-Я]{2,}\b[\s,]*){4,}")


def is_useless_paragraph(p: str) -> bool:
    """Абзацы, которые не несут смысла"""

    if len(p) < 20:
        return True

    if SECTION_ONLY_RE.match(p):
        return True

    if TOO_MANY_ABBR_RE.search(p):
        return True

    letters = sum(c.isalpha() for c in p)
    if letters / max(len(p), 1) < 0.3:
        return True

    return False


# def clean_paragraph(p: str) -> str:
#     p = p.strip()
#     p = re.sub(r"\s+", " ", p)
#     return p

def clean_paragraph(text: str) -> str | None:
    text = text.strip()

    if len(text) < 30:
        return None

    if re.fullmatch(r"[\d\.\-]+", text):
        return None

    digit_ratio = sum(c.isdigit() for c in text) / len(text)
    if digit_ratio > 0.6:
        return None

    if re.search(r"(.)\1{3,}", text):  # ссввяяззии
        return None

    text = re.sub(r"\s+", " ", text)
    return text


# =========================================================
# Sentence split (для длинных абзацев)
# =========================================================

def split_into_sentences(text: str) -> List[str]:
    text = text.replace("\n", " ")
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in sentences if len(s.strip()) > 5]


def split_and_clean_paragraphs(text: str) -> list[str]:
    raw = re.split(r"\n\s*\n", text)
    cleaned = []

    for p in raw:
        p = clean_paragraph(p)
        if p:
            cleaned.append(p)

    return cleaned


# =========================================================
# Core chunking logic
# =========================================================

def split_long_paragraph(
    paragraph: str,
    max_words: int = 120
) -> List[str]:
    """Если абзац слишком длинный — режем по предложениям"""
    words = paragraph.split()
    if len(words) <= max_words:
        return [paragraph]

    sentences = split_into_sentences(paragraph)
    chunks = []

    current = []
    current_len = 0

    for s in sentences:
        s_len = len(s.split())

        if current_len + s_len <= max_words:
            current.append(s)
            current_len += s_len
        else:
            if current:
                chunks.append(" ".join(current))
            current = [s]
            current_len = s_len

    if current:
        chunks.append(" ".join(current))

    return chunks


def merge_short_chunks(
    chunks: List[str],
    min_words: int = 60,
    max_words: int = 120
) -> List[str]:
    """Объединяем соседние слишком короткие чанки"""
    merged = []
    buffer = ""

    for chunk in chunks:
        chunk_len = len(chunk.split())

        if not buffer:
            buffer = chunk
            continue

        buffer_len = len(buffer.split())

        if buffer_len < min_words and buffer_len + chunk_len <= max_words:
            buffer = buffer + " " + chunk
        else:
            merged.append(buffer)
            buffer = chunk

    if buffer:
        merged.append(buffer)

    return merged


# =========================================================
# Public API
# =========================================================

def filter_content_pages(pages: List[Dict]) -> List[Dict]:
    content = [p for p in pages if p.get("page_type") == "content"]
    logger.info(f"Content pages: {len(content)} / {len(pages)}")
    return content


# def chunk_document(
#     pages: List[Dict],
#     min_words: int = 60,
#     max_words: int = 120,
# ) -> List[Dict]:

#     results = []

#     for page in pages:
#         raw_text = page.get("text", "")
#         if not raw_text:
#             continue

#         text = normalize_text(raw_text)
#         paragraphs = split_into_paragraphs(text)

#         cleaned = []
#         for p in paragraphs:
#             p = clean_paragraph(p)
#             if not is_useless_paragraph(p):
#                 cleaned.extend(split_long_paragraph(p, max_words=max_words))

#         cleaned = merge_short_chunks(
#             cleaned,
#             min_words=min_words,
#             max_words=max_words
#         )
def chunk_document(pages):
    faiss_chunks = []
    bm25_chunks = []

    for page in pages:
        paragraphs = split_and_clean_paragraphs(page["text"])

        faiss = build_faiss_chunks(paragraphs)
        bm25  = build_bm25_chunks(paragraphs)

    for idx, chunk in enumerate(faiss):
        faiss_chunks.append({
                "text": chunk,
                "chunk_id": idx,
                "page": page.get("page"),
                "path": page.get("path"),
                "file_type": page.get("file_type"),
                "sheet": page.get("sheet"),
                "section": page.get("section"),
                "type": page.get("page_type"),
            })
    
    for idx, chunk in enumerate(bm25):
        bm25_chunks.append({
                "text": chunk,
                "chunk_id": idx,
                "page": page.get("page"),
                "path": page.get("path"),
                "file_type": page.get("file_type"),
                "sheet": page.get("sheet"),
                "section": page.get("section"),
                "type": page.get("page_type"),
            })

    logger.info(f"Chunking finished: {len(faiss_chunks)} chunks")
    logger.info(f"Chunking finished: {len(bm25_chunks)} chunks")
    return faiss_chunks, bm25_chunks


def build_faiss_chunks(paragraphs, min_words=200, max_words=800):
    chunks = []
    current, cur_len = [], 0

    for p in paragraphs:
        w = len(p.split())

        if cur_len + w <= max_words:
            current.append(p)
            cur_len += w
        else:
            if cur_len >= min_words:
                chunks.append(" ".join(current))
                current, cur_len = [p], w
            else:
                current.append(p)
                cur_len += w

    if current:
        chunks.append(" ".join(current))

    return chunks


def build_bm25_chunks(paragraphs, min_len=150, max_len=300):
    chunks = []

    for p in paragraphs:
        if len(p) <= max_len:
            if len(p) >= min_len:
                chunks.append(p)
        else:
            sentences = split_into_sentences(p)
            buf = ""

            for s in sentences:
                if len(buf) + len(s) <= max_len:
                    buf += " " + s
                else:
                    if len(buf) >= min_len:
                        chunks.append(buf.strip())
                    buf = s

            if len(buf) >= min_len:
                chunks.append(buf.strip())

    return chunks
