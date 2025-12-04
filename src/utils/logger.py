
from loguru import logger

logger.add("logs/app.log", rotation="10 MB", compression="zip")

__all__ = ["logger"]
