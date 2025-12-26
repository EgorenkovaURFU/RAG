from config.config import Config
from pathlib import Path
import json
from loguru import logger


config = Config()


class DocRegistry:
    def __init__(self, path: str = config.paths['path_registry']):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.docs = self._load()

    def _load(self) -> dict:
        """Download registry from disk"""
        if not self.path.exists():
            logger.info("DocRegistry: file not found, creating new registry")
            return {}

        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load DocRegistry: {e}")
            return {}

    def _save(self):
        """Save registry to disk"""
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.docs, f, ensure_ascii=False, indent=2)


    def exists(self, doc_id, doc_hash):
        return (
            doc_id in self.docs and self.docs[doc_id]['hash'] == doc_hash
        )
    
    def register(self, doc_id, info):
        self.docs[doc_id] = info
        self._save()

