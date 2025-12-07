import docx
from pathlib import Path
from loguru import logger


def parse_docx(file_path: str) -> list:

    """
    Docstring for parse_docx
    
    :param file_path: Description
    :type file_path: str
    :return: Description
    :rtype: list
    """

    file_path = Path(file_path)
    logger.info(f'Parsing DOXC: {file_path}')

    try:
        doc = docx.Document(file_path)
    except Exception as ex:
        logger.error(f'Error during parsing DOCX {file_path}: {ex}')
        return []
    
    paregraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

    if not paregraphs:
        logger.warning(f'DOCX is empty: {file_path}')
        return []
    
    return [{
        'text': '\n'.join(paregraphs),
        'page': None,
        'path': str(file_path),
        'type': 'docx'
    }]

