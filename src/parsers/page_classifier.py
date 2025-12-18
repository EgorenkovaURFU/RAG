import re


def detect_page_type(text: str) -> str:
    """
    Classify PDF page by its content.
    
    Returns: 'title', 'toc', 'content'
    """

    if not text:
        return "empty"

    t = text.lower()

    # Оглавление / содержание
    if "оглавление" in t or "содержание" in t:
        return "toc"

    # Много точек и цифр — типичный признак оглавления
    dots_ratio = t.count('.') / max(len(t), 1)
    digits_ratio = sum(c.isdigit() for c in t) / max(len(t), 1)

    if dots_ratio > 0.05 and digits_ratio > 0.05:
        return "toc"

    # Очень короткие страницы — титульники
    # words = re.findall(r"\w+", t)
    # if len(words) < 80:
    #     return "title"

    return "content"
