from pathlib import Path
import csv
import re
from loguru import logger

from src.parsers.parse_manager import parse_document
from src.chunking.chunker import filter_content_pages


# =========================
# Paragraph-based chunking
# =========================

def split_into_paragraphs(text: str) -> list[str]:
    """
    Split text into meaningful paragraphs.
    """
    paragraphs = re.split(r"\n\s*\n", text)
    return [p.strip() for p in paragraphs if len(p.strip()) > 30]


def chunk_by_paragraphs(
    text: str,
    max_tokens: int = 500,
    min_tokens: int = 150,
) -> list[str]:
    """
    Build large chunks from paragraphs.
    """
    paragraphs = split_into_paragraphs(text)

    chunks = []
    current = []
    current_len = 0

    for p in paragraphs:
        p_len = len(p.split())

        if current_len + p_len <= max_tokens:
            current.append(p)
            current_len += p_len
        else:
            if current_len >= min_tokens:
                chunks.append("\n".join(current))
                current = [p]
                current_len = p_len
            else:
                # forcibly extend small chunk
                current.append(p)
                current_len += p_len

    if current:
        chunks.append("\n".join(current))

    return chunks


# =========================
# Main export logic
# =========================

def export_chunks_for_manual_labeling(
    input_dir: str,
    output_csv: str,
    max_tokens: int = 500,
):
    input_dir = Path(input_dir)
    rows = []

    logger.info(f"Scanning directory: {input_dir}")

    for file_path in input_dir.rglob("*"):
        if not file_path.is_file():
            continue

        logger.info(f"Parsing file: {file_path}")
        pages = parse_document(str(file_path))
        if not pages:
            continue

# ⚠️ Фильтрация только для PDF
        if file_path.suffix.lower() == ".pdf":
            pages = filter_content_pages(pages)


        for page in pages:
            if not isinstance(page, dict):
                logger.warning(f"Skip non-dict page in {file_path}")
                continue

            text = page.get("text", "").strip()

            if not text:
                continue

            chunks = chunk_by_paragraphs(text, max_tokens=max_tokens)

            for chunk in chunks:
                rows.append({
                    "path": page.get("path"),
                    "page": page.get("page"),
                    "chunk_text": chunk,
                    "type_chunk": ""
                })

    logger.info(f"Exporting {len(rows)} chunks to {output_csv}")

    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["path", "page", "chunk_text", "type_chunk"]
        )
        writer.writeheader()
        writer.writerows(rows)

    logger.success("Export finished successfully")


# =========================
# CLI entry point
# =========================

if __name__ == "__main__":
    export_chunks_for_manual_labeling(
        input_dir="data/raw/1c-data",
        output_csv="data/manual_chunks.csv",
        max_tokens=600,
    )
