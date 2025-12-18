import re
from loguru import logger


def filter_content_pages(pages: list) -> list:
    content = [p for p in pages if p.get("page_type") == "content"]
    logger.info(f"Content pages: {len(content)} / {len(pages)}")
    return content


def spllit_into_sentences(text: str) -> list:
    """
    Docstring for spllit_into_sentences
    
    :param text: Description
    :type text: str
    :return: Description
    :rtype: list
    """
    text = text.replace("\n", " ")
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in sentences if s.strip()]


def chunk_text(text: str, max_tokens: int = 500) -> list:
    """
    Docstring for chunk_text
    
    :param text: Description
    :type text: str
    :param max_tokens: Description
    :type max_tokens: int
    :return: Description
    :rtype: list
    """

    text = str(text)
    sentences = spllit_into_sentences(text)
    chunks = []

    current_chunk = []
    current_length = 0

    for sent in sentences:
        sent = str(sent)
        sent_len = len(sent.split())

        if current_length + sent_len < max_tokens:
            chunks.append(" ".join(current_chunk))
            current_chunk = [sent]
            current_length = sent_len
        else:
            current_chunk.append(sent)
            current_length += sent_len
    
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


def progress_document(parsed_pages: list, max_tokens=500) -> list:
    """
    Docstring for progress_document
    
    :param parsed_pages: Description
    :type parsed_pages: list
    :param max_tokens: Description
    :return: Description
    :rtype: list
    """
    if not parsed_pages:
        logger.warning("⚠️ Document skipped: no parsed pages")
        return []
    
    results = []
    logger.info(
        f"Starting chunking document: {parsed_pages[0].get('path', 'unknown')}"
    )

    for entry in parsed_pages:
        text = entry.get("text", "").strip()
        if not text:
            continue

        chunks = chunk_text(text, max_tokens=max_tokens)

        for idx, chunk in enumerate(chunks):
            results.append({
                "text": chunk,
                "page": entry.get("page"),
                "path": entry.get("path"),
                "type": entry.get("type"),
                "chunk_id": idx
            })

    if not results:
        logger.warning(
            f"Document produced no chunks: {parsed_pages[0].get('path', 'unknown')}"
        )

    logger.info(f"Chanking was finished: got {len(results)} chunks")
    return results


class TextSplitter:
    """
    """

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 0):
        self.max_tokens = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text: str) -> list[str]:
        return chunk_text(text, max_tokens=self.max_tokens)


# Test
if __name__ == "__main__":
    sample = [
        {
            "text": "This is an example text. It will be divided into several sentences.",
            "page": 1,
            "path": "test.pdf",
            "type": "pdf"
        }
    ]

    res = progress_document(sample)
    print(res)

