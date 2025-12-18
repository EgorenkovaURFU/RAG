from loguru import logger
import uuid

from src.parsers.pdf_parser import parse_pdf
from src.chunking.chunker import progress_document, filter_content_pages
from src.vector_store.bm25_store import BM25Store


PDF_PATH = "data/debug/test.pdf"


if __name__ == "__main__":
    logger.info("BM25 DEBUG STEP")

    # 1️⃣ Парсинг
    pages = parse_pdf(PDF_PATH)
    assert pages, "No pages parsed"

    pages = filter_content_pages(pages)
    assert pages, "No content pages"

    # 2️⃣ Чанкинг
    chunks = progress_document(pages)
    assert chunks, "No chunks"

    logger.info(f"Chunks produced: {len(chunks)}")

    # 3️⃣ Подготовка документов для BM25
    documents = []
    for c in chunks:
        documents.append({
            "text": c["text"],
            "metadata": {
                "id": str(uuid.uuid4()),
                "path": c["path"],
                "page": c["page"],
                "chunk_id": c["chunk_id"],
                "type": c["type"],
            }
        })

    # 4️⃣ Создание BM25
    bm25 = BM25Store()
    bm25.add(documents)

    logger.success("BM25 index built")

    # 5️⃣ Тестовый поиск
    query = "проверка трансмиссионной связи валов УЭЦН"
    results = bm25.search(query, top_k=5)

    print("\n" + "=" * 80)
    print("BM25 SEARCH RESULTS")
    print("=" * 80)

    for r in results:
        print(f"\nSCORE: {r['score']:.4f}")
        print(f"ID: {r['id']}")
        print(f"PAGE: {r['metadata']['page']}")
        print(r["text"][:300])
