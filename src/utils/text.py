import re

SAFE_STOP_WORDS = {
    "и", "в", "во", "на", "с", "к", "о",
    "а", "но", "или", "что", "это",
    "как", "так", "же", "то",
    "из", "от", "по"
}

def bm25_tokenize(text: str) -> list[str]:
    text = text.lower()

    tokens = re.findall(r"[а-яa-z0-9\-]+", text)

    return [
        t for t in tokens
        if t not in SAFE_STOP_WORDS and len(t) > 1
    ]