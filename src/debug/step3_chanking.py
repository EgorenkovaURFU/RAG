from src.parsers.pdf_parser import parse_pdf
from src.chunking.chunker import filter_content_pages, progress_document

pages = parse_pdf("data/debug/test.pdf")
#pages = filter_content_pages(pages)
chunks = progress_document(pages)

print(f"TOTAL CHUNKS: {len(chunks)}\n")

for c in chunks:
    print("=" * 80)
    print(f"PAGE {c['page']} | CHUNK {c['text']}")
    print(c["text"])