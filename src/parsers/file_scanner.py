import os
from pathlib import Path
from loguru import logger


#TODO сделать фильтацию  по подпапкам и по дате изменения
ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.xlsx', '.txt'} # , 


def scan_raw_data(root_dir: str = 'data/raw') -> list:
    """
    Role:
        File search on disk, filtering by extension.

    Functionality:
        * Recursive directory traversal
        * Exceptions (temp, ~$, .git, etc.)
        * Returning a list of files with paths

    Does not:
        * Parsing
        * Reading contents
    
    :param root_dir: Path to dir
    :type root_dir: str
    :return: List of files with paths
    :rtype: list
    """

    files_list = []

    root_path = Path(root_dir)
    if not root_path.exists():
        logger.warning(f"The directory {root_path} was not found.")
        return files_list
    
    logger.info(f"Scanning the directory {root_dir}")

    for dirpath, _, filenames in os.walk(root_path):
        for file in filenames:
            file_path = Path(dirpath) / file
            if file_path.suffix.lower() in ALLOWED_EXTENSIONS:
                files_list.append(str(file_path))
                logger.info(f'Tha file has been found: {file_path}')
            else:
                logger.debug(f'The file has passed: {file_path}')
    
    logger.info(f'Total liles found: {len(files_list)}')

    return files_list


if __name__ == '__main__':
    files = scan_raw_data()
    print("\nFiles found:")
    for f in files:
        print(f' - {f}')

