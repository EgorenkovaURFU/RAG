from pathlib import Path
import yaml

class Config:
    def __init__(self, path: str = "config/config.yaml"):
        self.path = Path(path)
        self._load()

    def _load(self):
        with open(self.path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        self.paths = data["paths"]
        self.retrieval = data["retrieval"]
        self.chunking = data["chunking"]
        self.embeddings = data["embeddings"]
        self.llm = data["llm"]
        self.prompt = data["prompt"]
