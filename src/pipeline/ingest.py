from pathlib import Path
from loguru import logger
import uuid

from src.parsers.pdf_parser import parse_pdf
from src.parsers.parse_manager import parse_documant
from src.parsers.file_scanner import scan_raw_data
from src.chunking.chunker import progress_document, filter_content_pages
from src.embeddings.embedder import Embedder
from src.vector_store.faiss_store import FaissStore
from src.vector_store.bm25_store import BM25Store




BATCH_SIZE = 256


def ingest_directory(root_folder="data/raw/1c-data"):
    root = Path(root_folder)

    if not root.exists():
        logger.error(f"Folder not found: {root}")
        return

    logger.info(f"Start ingest from {root.resolve()}")

    embedder = Embedder()
    store = FaissStore(
        dim=384,#embedder.dim,   # или 384, если у тебя фиксировано
        index_dir="data/faiss")
    bm25 = BM25Store()

    files = scan_raw_data(root_dir=root_folder)

    total_files = 0
    total_chunks = 0

    for path in files:
        logger.info(f"Processing: {path}")
        total_files += 1

        try:
            pages = parse_documant(path)
        except Exception as e:
            logger.error(f"Failed to parse {path}: {e}")
            continue

        if not pages:
            logger.warning(f"No content parsed: {path}")
            continue

        # 2️⃣ Фильтрация страниц
        pages = filter_content_pages(pages)
        if not pages:
            logger.warning(f"No content pages after filtering: {path}")
            continue

        # 3️⃣ Чанкинг
        chunks = progress_document(pages)
        if not chunks:
            logger.warning(f"No returned chunks: path {path}")
            continue
        
        ids = []
        texts = []
        metadatas = []

        for c in chunks:
            uid = str(uuid.uuid4())
            ids.append(uid)
            texts.append(c["text"])
            metadatas.append({
                "id": uid,
                "path": c["path"],
                "page": c["page"],
                "chunk_id": c["chunk_id"],
                "type": c["type"],})

        embeddings = embedder.embed(texts)

        store.add(
            ids=ids,
            embeddings=embeddings,
            texts=texts,
            metadatas=metadatas,
        )

        bm25.add(
            texts=texts,
            metadatas=metadatas,
            )

        total_chunks += len(texts)


    store.save()
    bm25.save("data/bm25_index.pkl")


    logger.success(
        f"Done. Files: {total_files}, chunks: {total_chunks}"
    )


if __name__ == "__main__":
    ingest_directory()
