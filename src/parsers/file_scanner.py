import os
from pathlib import Path
from loguru import logger


#TODO сделать фильтацию  по подпапкам и по дате изменения
ALLOWED_EXTENSIONS = {'.pdf', } # '.docx', '.xlsx', '.txt'


def scan_raw_data(root_dir: str = 'data/raw') -> list:
    """
    Docstring for scan_raw_data
    
    :param root_dir: Description
    :type root_dir: str
    :return: Description
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

