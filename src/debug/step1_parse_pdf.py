from src.parsers.pdf_parser import parse_pdf
from loguru import logger

pages = parse_pdf("data/debug/test.pdf")

logger.info(f"Parsed {len(pages)} pages")

for p in pages:
    print("=" * 50)
    print(f"PAGE {p['page']} | TYPE = {p['page_type']}")
    print(p["text"][:400])

    