from pathlib import Path
from loguru import logger

from .pdf_parser import parse_pdf
from .docx_parser import parse_docx
from .excel_parser import parse_excel
from .txt_parser import parse_txt


def parse_document(file_path: str) -> list:
    file_path = Path(file_path)

    if not file_path.exists():
        logger.warning(f"File not found: {file_path}")
        return []

    if not file_path.is_file():
        logger.warning(f"Not a file: {file_path}")
        return []

    ext = file_path.suffix.lower()

    if ext == '.pdf':
        return parse_pdf(file_path)
    
    elif ext == '.docx':
        return parse_docx(file_path)
    
    elif ext == '.xlsx':
        return parse_excel(file_path)
    
    elif ext == '.txt':
        return parse_txt(file_path)
    
    else:
        logger.warning(f'Unexpected format: {file_path}')
        return []
    
