from src.embeddings.embedder import Embedder
from src.vector_store.chroma_store import ChromaStore
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from loguru import logger


class RAGPipeline:

    def __init__(
            self,
            embed_model='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',
            llm_model='sberbank-ai/rugpt3small_based_on_gpt2',
            device=None,
            top_k=3
                 ):
        
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        
