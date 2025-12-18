import shutil
import textwrap
import subprocess
from typing import List, Tuple

from loguru import logger
from src.embeddings.embedder import Embedder
from src.vector_store.faiss_store import FaissStore
from src.vector_store.bm25_store import BM25Store
from src.search.hybrid_search import hybrid_search
from src.reranker.reranker import Reranker
from src.llm.postprocessing import postprocess_answer
import os
from collections import defaultdict


MODEL = "bambucha/saiga-llama3"
TOP_K=5
MAX_CONTEXT_CHARS=4000
OLLAMA_EXE_CANDIDATES = [
    r"C:\Users\tatya\AppData\Local\Programs\Ollama\Ollama.exe",
    r"C:\Program Files\Ollama\Ollama.exe",
    'ollama'
]


def detect_ollama_executable() -> str:
    """
    Try to find ollama.exe: check the candidats and PATH (shutil.which)
    
    :return: PATH of ollama executable
    :rtype: str
    """

    logger.info("Checking candidates:")
    for path in OLLAMA_EXE_CANDIDATES:
        logger.info("  testing:", path)
        if os.path.exists(path):
            logger.info("FOUND:", path)
            return path
    raise FileNotFoundError(
        'ollama.exe was not found. Install Ollama and add to PATH or write the path into OLLAMA_EXE_CANDIDATES'
    )

def smart_truncate(text: str, max_chars: int = 1500) -> str:
    """
    Cut texts at sentence/line boundaries without cutting it in the middle.
    Return safe, abbreviated text (with a trailing "..." if truncated).
    
    :param text: Description
    :type text: str
    :param max_chars: Description
    :type max_chars: int
    :return: Description
    :rtype: str
    """

    if not text:
        return text
    
    if len(text) <= max_chars:
        return text

    truncated = text[:max_chars]

    end_marks = ['\n', '. ', '! ', '? ', '—', '–', '; ']
    last_good = max(truncated.rfind(m) for m in end_marks)

    if last_good <= 0:
        last_space = truncated.rfind(' ')
        if last_space > 0:
            return truncated[:last_space].rstrip() + "..."
        return truncated.rstrip() + "..."

    return truncated[:last_good + 1].rstrip() + "..."


def build_prompt_str(context_texts: List[str], question: str) -> str:
    """
    Create a strict prompt. 
    Insert contexts and a question.
    Limit the overrall size.
    
    :param context_texts: Description
    :type context_texts: List[str]
    :param question: Description
    :type question: str
    :return: Description
    :rtype: str
    """

    header = (
        'Ты - ассистент, который отвечает только на основе предоставленного контекста.\n'
        'Если информации недостаточно, коротко напиши: \'недостаточно данных\' и объясни причину, если это возможно.\n'
        'Не придумывай фактов.\n\n'
    )

    context_combined = "\n\n---\n\n".join(context_texts)



    # if len(context_combined) > MAX_CONTEXT_CHARS:
    #     context_combined = context_combined[:MAX_CONTEXT_CHARS]
    #     last_space = context_combined.rfind(' ')
    #     if last_space > 0:
    #         context_combined = context_combined[:last_space] + '...'

    context_combined = smart_truncate(text=context_combined, max_chars = 1500)
        
    prompt = (
        header +
        'Контекст:\n' +
        context_combined + 
        '\n\nВопрос\n\n' +
        question +
        '\n\nОтвет:\n'
        )
    return prompt


def merge_neighbor_chunks(docs: List[str], metas: List[dict], window_size: int = 1) -> Tuple[List[str], List[dict]]:
    """
    Docstring for merge_neighbor_chunks
    
    :param docs: Description
    :type docs: List[str]
    :param metas: Description
    :type metas: List[dict]
    :param window_size: Description
    :type window_size: int
    :return: Description
    :rtype: Tuple[List[str], List[dict]]
    """

    if not docs or not metas:
        return [], []
    
    groups = defaultdict(list)

    for idx, m in enumerate(metas):
        src = m.get('source') or m.get('path') or 'unknown'
        chunk_id = m.get('chunk', idx)
        groups[src].append((chunk_id, idx, docs[idx], m))

    merged_docs = []
    merged_metas = []

    for src, items in groups.items():
        items.sort(key=lambda x: (x[0], x[1]))

        for pos in range(len(items)):
            window_texts = []
            for k in range(window_size, 0, -1):
                i = pos - k
                if i >= 0:
                    window_texts.append(items[i][2])
            window_texts.append(items[pos][2])
            for k in range(1, window_size + 1):
                i = pos + k
                if i < len(items):
                    window_texts.append(items[i][2])

            merge_text = '\n\n'.join(window_texts)
            merged_docs.append(merge_text)
            merged_metas.append(items[pos][3])

    return merged_docs, merged_metas
        

def format_sources(metas: List[dict]) -> str:
    """
    Docstring for format_sources
    
    :param metas: Description
    :type metas: List[dict]
    :return: Description
    :rtype: str
    """
    lines = []
    for m in metas:
        src_path = m.get('path') or m.get('source') or 'unknown'
        src = os.path.basename(src_path)
        page = m.get('page')
        chunk = m.get('chunk')
        extra = []
        if isinstance(page, (list, tuple)):
            extra.append(f'стр. {page[0]}-{page[-1]}')
        elif page is not None:   # может здесь лучше else??????????????????
            extra.append(f'стр. {page}') 
        if chunk is not None:
            extra.append(f'чанк {chunk}')
        if extra:
            lines.append(f"- {src} ({', '.join(extra)}) — {src_path}")
        else:
            lines.append(f"- {src} — {src_path}")
    return '\n'.join(lines)


def run_ollama_via_clients(model: str, prompt: str) -> str:
    """
    Try to use Python Client ollama.
    If it doesn't work, raise exception to swich on subprocess.
    
    :param model: Description
    :type model: str
    :param prompt: Description
    :type prompt: str
    :return: Description
    :rtype: str
    """

    try:
        from ollama import Client
    except Exception as e:
        raise RuntimeError("Ollama Python Client is not available") from e
    
    client = Client()
    messages = [{'role': 'user', 'content': prompt}]
    resp = client.chat(model=model, messages=messages)
    return resp['message']['content']


def run_ollama_via_subprocess(ollama_exe: str, model: str, prompt: str) -> str:
    """
    Run ollama using subprocess.
    Use 'ollama run <model> <prompt>.
    Return stdout (decoding utf-8).
    
    :param ollama_exe: Description
    :type ollama_exe: str
    :param model: Description
    :type model: str
    :param prompt: Description
    :type prompt: str
    :return: Description
    :rtype: str
    """

    cmd = [ollama_exe, 'run', model]
    logger.info(f'Run subprocess: {' '.join(cmd[:3])}...(hidden prompt)')
    proc = subprocess.run(cmd, input=prompt.encode('utf-8'), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out = proc.stdout.decode('utf-8', errors='ignore').strip()
    err = proc.stderr.decode('utf-8', errors='ignore').strip()
    if err:
        logger.debug(f'Ollama stderr: {err[:1000]}')
    return out


class RAGPipeline:

    def __init__(self, model: str = MODEL, top_k: int = TOP_K):
        self.embedder = Embedder()
        self.faiss_store = FaissStore(dim=384)
        self.bm25_store = BM25Store().load()
        self.reranker = Reranker()
        self.model = model
        self.top_k = top_k

        try:
            self.ollama_exe = detect_ollama_executable()
        except FileExistsError as e:
            logger.warning(str(e))
            self.ollama_exe = None

        try:
            import ollama as _o
            self.ollama_client_available = True
        except Exception:
            self.ollama_client_available = False

        logger.info(f'RAGPipeline is inited. model={self.model} top_k={self.top_k}, ollama_client={self.ollama_client_available}, ollama_exe={self.ollama_exe}')

    def retrieve(self, query: str):

        q_emb = self.embedder.embed(query)[0]

        results = hybrid_search(
            query=query,
            query_embedding=q_emb,
            faiss_store=self.faiss_store,
            bm25_store=self.bm25_store,
            top_k=self.top_k * 2)
        
        unique = {}
        for r in results:
            key = r["metadata"]["chunk_id"]
            unique[key] = r

        results = list(unique.values())

        
        if self.reranker:
            texts = [r["text"] for r in results]
            reranked_texts = self.reranker.rerank(query, texts, top_k=self.top_k)

            text2res = {r["text"]: r for r in results}
            results = [text2res[t] for t in reranked_texts]
        else:
            results = results[:self.top_k]
        
        docs = [r["text"] for r in results]
        metas = [r["metadata"] for r in results]

        return docs, metas

        # res as usual structure: dict with key 'documents' and 'metadatas'
        # try:
        #     docs = res['documents'][0] if res['documents'] else []
        #     metas = res['metadatas'][0] if res['metadatas'] else []
        # except Exception:
        #     logger.warning('Unexpected result format from Chroma.query, returning empty.')
        #     return [], []
        
        # if not docs:
        #     return [], []
        
        # return docs, metas
        
        # # reranking
        # top_docs = self.reranker.rerank(query, docs, top_k=self.top_k)

        # final_metas = []
        # for doc in docs:
        #     idx = docs.index(doc)
        #     metas.append(metas[idx])

        # return top_docs, final_metas

    def _prepare_context(self, results):
        docs = [r["text"] for r in results]
        metas = [r["metadata"] for r in results]
        return docs, metas

    
    def generate(self, question: str) -> Tuple[str, List[dict]]:
        docs, metas = self.retrieve(question)
        
        if not docs:
            return 'По запросу нет релевантных документов', []
        
        docs, metas = merge_neighbor_chunks(docs, metas, window_size=5)

        docs = docs[:6]
        metas = metas[:6]

        # build context and prompt
        prompt = build_prompt_str(docs, question)

        # Try to call through the client if available
        if self.ollama_client_available:
            try:
                logger.info('Try to call ollama through Python client...')
                answer = run_ollama_via_clients(self.model, prompt)
                processed = postprocess_answer(answer)
                return processed, metas
            except Exception as e:
                logger.warning(f'Ollama client faild: {e}. Lets move on subprocess fallback')

        if self.ollama_exe:
            try:
                answer = run_ollama_via_subprocess(self.ollama_exe, self.model, prompt)
                processed = postprocess_answer(answer)
                return processed, metas
            except Exception as e:
                logger.error(f'Subprocess call to ollama failed: {e}')
                return 'Ошибка при вызове Ollama', metas
        
        return 'Ollama не настроен (нет клиета и не найден ollama.exe).', metas
    
    

if __name__=='__main__':
    import sys

    logger.info('Start RAG pipeline (CLI test)')
    pipeline = RAGPipeline()
    if len(sys.argv) > 1:
        q = ' '.join(sys.argv[1:])
    else:
        q = input('Вопрос: ').strip()

    answer , sources = pipeline.generate(q)
    print('\n=== ОТВЕТ ===\n')
    print(answer.strip())
    if sources:
        print('\n=== ИСТОЧНИКИ ===\n')
        print(format_sources(sources))

