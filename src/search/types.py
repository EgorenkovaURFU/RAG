from typing import TypedDict, Literal, Dict, Any


class SearchResult(TypedDict):
    id: str
    score: float
    norm_score: float
    source: Literal['faiss', 'bm25', 'hybrid']
    text: str
    metadata: Dict[str, Any]

