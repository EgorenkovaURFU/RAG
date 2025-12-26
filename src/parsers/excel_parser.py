import pandas as pd
from pathlib import Path
from loguru import logger
from src.parsers.page_classifier import detect_page_type


def parse_excel(file_path: str) -> list:

    """
    Role: Extracting text from XLS/XLSX.
    Functionality: Returns text from cells and metadata (path, file_type, page, sheet, section, page_type)

    :param file_path: Path to file
    :type file_path: str
    :return: Text and metadata
    :rtype: list
    """

    file_path = Path(file_path)
    logger.info(f'Parsing excel: {file_path}')

    results = []

    try:
        xls = pd.ExcelFile(file_path)
    except Exception as ex:
        logger.error(f'Error during parsing Excel file {file_path}: {ex}')
        return []
    
    for sheet in xls.sheet_names:
        df = pd.read_excel(file_path, sheet_name=sheet, dtype=str).fillna("")

        for row in df.itertuples(index=False):
            text = " | ".join(map(str, row))

            if text.strip():
                results.append({
                    'text': text,
                    'path': str(file_path),
                    'file_type': 'xlsx',

                    'page': None,
                    'sheet': sheet,
                    'section': None,

                    'page_type': None}
                    )
    
    return results

