from pathlib import Path
from loguru import logger
from src.parsers.page_classifier import detect_page_type


def parse_txt(file_path: str) -> list:
    file_path = Path(file_path)
    logger.info(f'Prsing TXT fife: {file_path}')

    try:
        text = file_path.read_text(encoding='utf-8', errors='ignore')
    except:
        text = file_path.read_text(encoding='utf-8', errors='ignore')

    return {
        'text': text,
        'path': str(file_path),
        'file_type': 'txt',

        'page': None,
        'sheet': None,
        'section': None,

        'page_type': None}

