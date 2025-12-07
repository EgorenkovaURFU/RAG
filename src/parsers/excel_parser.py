import pandas as pd
from pathlib import Path
from loguru import logger


def parse_excel(file_path: str) -> list:

    """
    Docstring for parse_excel
    
    :param file_path: Description
    :type file_path: str
    :return: Description
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
                    'page': sheet,
                    'path': str(file_path),
                    'type': 'xlsx'
                })
    
    return results

