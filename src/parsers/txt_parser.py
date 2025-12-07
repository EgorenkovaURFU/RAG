from pathlib import Path
from loguru import logger


def parse_txt(file_path: str) -> list:
    file_path = Path(file_path)
    logger.info(f'Prsing TXT fife: {file_path}')

    try:
        text = file_path.read_text(encoding='utf-8', errors='ignore')
    except:
        text = file_path.read_text(encoding='utf-8', errors='ignore')

    return [{
        'text': text,
        'page': None,
        'path': str(file_path),
        'type': 'txt'
    }]

