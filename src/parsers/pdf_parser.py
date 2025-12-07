import pdfplumber
from loguru import logger
from pathlib import Path


def parse_pdf(file_path: str) -> list:

    """
    Docstring for parse_pdf
    
    :param file_path: path to PDF-file
    :type file_path: str
    :return: List of Dicts with keys: 'text', 'page', 'path', 'type'
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
                    'page': page_num,
                    'path': str(file_path),
                    'type': 'pdf'
                })
    except Exception as ex:
        logger.info(f'Error during parsing PDF {file_path}: {ex}')

    logger.info(f'Done: extracted {len(results)} страниц.')
    
    return results


