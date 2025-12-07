from pathlib import Path
from loguru import logger

from .pdf_parser import parse_pdf
from .docx_parser import parse_docx
from .excel_parser import parse_excel
from .txt_parser import parse_txt


def parse_documant(file_path: str) -> list:
    ext = Path(file_path).suffix.lower()

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
    
