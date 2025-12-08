from src.parsers.file_scanner import scan_raw_data
from src.parsers.parse_manager import parse_documant
from src.chunking.chunker import progress_document

from src.embeddings.embedder import Embedder
from src.vector_store.chroma_store import ChromaStore

from loguru import logger
import uuid



def build_vector_store():
    logger.info('Start ')

    files = scan_raw_data(root_dir='rag/data/raw')

    embedder = Embedder()
    store = ChromaStore()

    all_texts = []
    all_embeddings = []
    all_matadata = []
    all_ids = []

    for file_path in files:
        pages = parse_documant(file_path)
        chunks = progress_document(pages)

        for ch in chunks:
            text = ch['text']
            metadata = {
                'path': ch['path'],
                'page': ch['page'],
                'type': ch['type'],
                'chunk': ch['chunk_id']
            }

            all_texts.append(text)
            all_matadata.append(metadata)
            all_ids.append(str(uuid.uuid4))

    logger.info('Generating embeddings...')
    all_embeddings = embedder.embed(all_texts)

    store.add(
        ids=all_ids,
        embeddings=all_embeddings,
        documents=all_texts,
        metadatas=all_matadata
    )

    logger.info('Vector database is installed successfully')

    