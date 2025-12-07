from pathlib import Path
from loguru import logger
import yaml


# The project structure

DIRS = [
    "data/raw",
    "data/processed",

    "src/parsers",
    "src/indexing",
    "src/search",
    "src/llm",
    "src/ui",

    "models",
    "chroma",
    "logs",
    "scripts",
]


# Create directities

def create_directories():
    logger.info("Create project structure...")

    for d in DIRS:
        path = Path(d)
        if not path.exists():
            path.mkdir(parents=True)
            logger.info(f"Created: {d}")
        else:
            logger.info(f"Already existed: {d}")


# Add __init__.py in to all src moduls

def create_init_files():
    logger.info("Creating __init__.py ...")

    src_dirs = [
        "src",
        "src/parsers",
        "src/chunking",
        "src/indexing",
        "src/search",
        "src/llm",
        "src/ui",
    ]

    for folder in src_dirs:
        init_path = Path(folder) / "__init__.py"
        if not init_path.exists():
            init_path.write_text("")
            logger.info(f"Added {init_path}")
        else:
            logger.info(f"{init_path} is alredy existed")


# Create config.yaml

def create_config():
    config = {
        "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
        "chunk_size": 500,
        "chunk_overlap": 50,
        "chroma_path": "chroma",
        "log_level": "INFO",
        "device": "cuda"
    }

    config_path = Path("config.yaml")

    if not config_path.exists():
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(config, f, allow_unicode=True)
        logger.info("The file config.yaml is created")
    else:
        logger.info("config.yaml is already existed")


# Create venv

def create_env():
    env_path = Path("venv")

    if not env_path.exists():
        env_path.write_text(
            "# Переменные окружения\n"
            "OPENAI_API_KEY=\n"
            "HF_TOKEN=\n"
        )
        logger.info("The file venv has been created")
    else:
        logger.info("venv alresdy existed")


# Create the base logger

def create_logger():
    logger_file = Path("src/utils/logger.py")

    if not logger_file.exists():
        logger_file.parent.mkdir(parents=True, exist_ok=True)
        logger_file.write_text(
            """
from loguru import logger

logger.add("logs/app.log", rotation="10 MB", compression="zip")

__all__ = ["logger"]
"""
        )
        logger.info("The base logger was created: rag/src/utils/logger.py")
    else:
        logger.info("logger.py already exist")


# The main func

if __name__ == "__main__":
    logger.info("🚀 Запуск setup_project.py")

    create_directories()
    create_init_files()
    create_config()
    create_env()
    create_logger()

    logger.info("The project sucseefully was created!")
