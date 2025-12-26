import pdfplumber
from loguru import logger
from pathlib import Path
from src.parsers.page_classifier import detect_page_type


def parse_pdf(file_path: str) -> list:

    """
    Role: Extracting information from a PDF document.
    Functionality: Returns text from a page and metadata (path, file_type, page, sheet, section, page_type)

    :param file_path: path to PDF-file
    :type file_path: str
    :return: List of Dicts with keys: 'text', 'file_type', 'page', 'sheet', 'section', 'page_type'
    :rtype: list
    """

    file_path = Path(file_path)

    results = []
    logger.info(f'Starting to parse PDF file: {file_path}')

    try:
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                text = page.extract_text()

                if not text:
                    logger.warning(f'There is not text on the page {page_num} ({file_path})')
                    continue

                results.append({
                    'text': text,
                    'path': str(file_path),
                    'file_type': 'pdf',

                    'page': page_num,
                    'sheet': None,
                    'section': None,

                    'page_type': detect_page_type(text)}
                    )
    except Exception as ex:
        logger.info(f'Error during parsing PDF {file_path}: {ex}')

    logger.info(f'Done: extracted {len(results)} страниц.')
    
    return results


