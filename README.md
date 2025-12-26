# RAG-system

## Instalation

## Using

## Data

## Structure

 - /app/
 - /data/
 - /src/ - auxiliary functions
   * parsers/ - Extracts raw text and basic metadata from various file types (PDF, DOCX, XLSX, TXT) without chunking, embedding, or searching.
        ** scan_raw_data.py: 
            Role: File search on disk, filtering by extension.
            Functionality:
                * Recursive directory traversal
                * Exceptions (temp, ~$, .git, etc.)
                * Returning a list of files with paths
        ** pdf_parser.py:
            Role: Extracting information from a PDF document.
            Functionality: Returns text from a page and metadata (path, file_type, page, sheet, section, page_type)
        ** docx_parser.py:
            Role: Extracting text from DOCX.
            Functionality: Extracting text by paragraphs, returns text and metadata (path, file_type, page, sheet, section, page_type)
        ** excel_pareser.py 
            Role: Extracting text from XLS/XLSX.
            Functionality: Returns text from cells and metadata (path, file_type, page, sheet, section, page_type)
            
