A = 1

from sentence_transformers import SentenceTransformer
import torch
from loguru import logger


class Embedder:

    def __init__(self, model_name='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'):
        logger.info(f'Download model: {model_name}')

        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model = SentenceTransformer(model_name, device=self.device)

        logger.info(f'The model run on device: {self.device}')

    def embed(self, texts: list) -> list:
        """
        Docstring for embed
        
        :param self: Description
        :param text: Description
        :type text: list
        :return: Description
        :rtype: list
        """

        if isinstance(texts, str):
            texts = [texts]

        return self.model.encode(
            texts, 
            batch_size=32, 
            convert_to_numpy=True,
            show_progress_bar=False
        )

