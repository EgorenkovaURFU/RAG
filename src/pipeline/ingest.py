from pathlib import Path
from loguru import logger
import uuid
import time

from src.parsers.parse_manager import parse_document
from src.parsers.file_scanner import scan_raw_data
from src.chunking.chunker import filter_content_pages # progress_document,
from src.embeddings.embedder import Embedder
from src.vector_store.faiss_store import FaissStore
from src.vector_store.bm25_store import BM25Store
from src.utils.hash import file_hash
from src.ingestion.doc_registry import DocRegistry
from config.config import Config
# from src.chunking.chunker import chunk_document_by_paragraphs
from src.chunking.chunker import chunk_document, filter_content_pages, chunk_document
from src.chunking.bm25_chanking import chunk_document_for_bm25


config = Config()

def log_chunk_stats(name, chunks):
    if not chunks:
        logger.info(f"{name}: no chunks")
        return

    lengths = [len(c["text"].split()) for c in chunks]
    logger.info(
        f"{name} stats: count={len(lengths)}, "
        f"avg_words={sum(lengths) // len(lengths)}, "
        f"min={min(lengths)}, max={max(lengths)}"
    )



def ingest_directory(root_folder='data/raw/1c-data'): #config.paths['data_dir']):
    root = Path(root_folder)

    if not root.exists():
        logger.error(f"Folder not found: {root}")
        return

    logger.info(f"Start ingest from {root.resolve()}")

    embedder = Embedder()
    store = FaissStore(dim=config.embeddings['dim'], index_dir=config.paths['faiss_dir'])
    bm25 = BM25Store()
    registry = DocRegistry()

    files = scan_raw_data(root_dir=root_folder)

    indexed_files = 0
    total_chunks = 0

    for path in files:
        path = Path(path)

        if not path.is_file():
            logger.warning(f"Skip non-file path: {path}")
            continue

        logger.info(f"Processing: {path}")
        indexed_files += 1

        doc_id = str(uuid.uuid5(
            uuid.NAMESPACE_URL,
            str(Path(path).resolve())))
        doc_hash = file_hash(path)
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # try:
        #     pages = parse_document(path)
        #     logger.info(
        #             f"[DEBUG] Parsed pages: {len(pages)} | "
        #             f"type={type(pages)} | "
        #             f"sample={pages[0].keys() if pages and isinstance(pages[0], dict) else pages[:1]}")
        # except Exception as e:
        #     logger.error(f"Failed to parse {path}: {e}")
        #     continue

    #     if registry.exists(doc_id, doc_hash):
    #         logger.info(f"SKIP unchanged document: {path}")
    #         continue
    #     else:
            # Парсинг
        try:
            pages = parse_document(path)

            logger.info(
                    f"[DEBUG] Parsed pages: {len(pages)} | "
                    f"type={type(pages)} | "
                    f"sample={pages[0].keys() if pages and isinstance(pages[0], dict) else pages[:1]}")
        except Exception as e:
                logger.error(f"Failed to parse {path}: {e}")
                continue

        if not pages:
                logger.warning(f"No content parsed: {path}")
                continue

            # Фильтрация страниц
        pages = filter_content_pages(pages)
        if not pages:
                logger.warning(f"No content pages after filtering: {path}")
                continue

            # Чанкинг
            #chunks = progress_document(pages)
        # chunks = chunk_document_by_paragraphs(pages, max_tokens=600)
        faiss_chunks, _ = chunk_document(pages)
        bm25_chunks =  chunk_document_for_bm25(pages)

        if not faiss_chunks and not bm25_chunks:
            logger.warning(f"No chunks after chunking & cleaning: {path}")
            continue

        log_chunk_stats("FAISS", faiss_chunks)
        log_chunk_stats("BM25", bm25_chunks)

        if faiss_chunks:
            faiss_ids = []
            faiss_texts = []
            faiss_metadatas = []

            for c in faiss_chunks:
                faiss_ids.append(str(uuid.uuid4()))
                faiss_texts.append(c["text"])
                faiss_metadatas.append({
                    "doc_id": doc_id,
                    "path": c["path"],
                    "file_type": c["file_type"],
                    "sheet": c["sheet"],
                    "page": c["page"],
                    "section": c["section"],
                    "chunk_id": c["chunk_id"],
                    "type": c["type"],
                })

            embeddings = embedder.embed(faiss_texts)

            store.add(
                ids=faiss_ids,
                embeddings=embeddings,
                texts=faiss_texts,
                metadatas=faiss_metadatas)
            
        if bm25_chunks:
            bm25_texts = []
            bm25_metadatas = []

            for c in bm25_chunks:
                bm25_texts.append(c["text"])
                bm25_metadatas.append({
                    "doc_id": doc_id,
                    "path": c["path"],
                    "file_type": c["file_type"],
                    "sheet": c["sheet"],
                    "page": c["page"],
                    "section": c["section"],
                    "chunk_id": c["chunk_id"],
                    "type": c["type"]})

            bm25.add(
                texts=bm25_texts,
                metadatas=bm25_metadatas)

        # faiss_texts = [c["text"] for c in faiss_chunks]
        # bm25_texts  = [c["text"] for c in bm25_chunks]

        
        # lengths = [len(c["text"].split()) for c in chunks]

        # if not lengths:
        #     logger.warning(
        #         f"No chunks after chunking & cleaning: {path}"
        #     )
        #     continue

        # logger.info(
        #     f"Chunks stats: count={len(lengths)}, "
        #     f"avg_words={sum(lengths) // len(lengths)}, "
        #     f"min={min(lengths)}, max={max(lengths)}")

        # if not chunks:
        #     logger.warning(f"No returned chunks: path {path}")
        #     continue
            
        # ids = []
        # texts = []
        # metadatas = []

        # for c in chunks:
        #     uid = str(uuid.uuid4())
        #     ids.append(uid)
        #     texts.append(c["text"])
        #     metadatas.append({
        #             "doc_id": doc_id,
        #             "path": c["path"],
        #             "file_type": c["file_type"],
        #             "sheet": c["sheet"],
        #             "page": c["page"],
        #             "section": c["section"],
        #             "chunk_id": c["chunk_id"],
        #             "type": c["type"],})

        # embeddings = embedder.embed(texts)

        # store.add(
        #         ids=ids,
        #         embeddings=embeddings,
        #         texts=texts,
        #         metadatas=metadatas,
        #     )

        # bm25.add(
        #         texts=texts,
        #         metadatas=metadatas)
            
        #     # registry.register(
        #     #     doc_id,
        #     #     {
        #     #         "hash": doc_hash,
        #     #         "path": str(path),
        #     #         "file_type": Path(path).suffix,
        #     #         "updated_at": time.time(),
        #     #     }
        #     # )

        # total_chunks += len(texts)
        total_chunks += len(faiss_chunks) + len(bm25_chunks)

    store.save()
    bm25.save("data/bm25_index.pkl")


    logger.success(
        f"Done. Files: {indexed_files}, chunks: {total_chunks}"
    )


if __name__ == "__main__":
    ingest_directory()
