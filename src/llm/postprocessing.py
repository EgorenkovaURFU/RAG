import re

def cleanup_answer(text: str) -> str:
    """
    Удаляет мусор, повторы и стандартные LLM-фразы.
    """

    patterns = [
        r"как модель[^.]+\.?",
        r"как ассистент[^.]+\.?",
        r"я основан на модели[^.]+\.?",
        r"исходя из предоставленного контекста[:, ]*",
        r"в предоставленном контексте[:, ]*",
        r"на основе контекста[:, ]*",
        r"привет[^.!\n]+[\n.!]?",
    ]

    for p in patterns:
        text = re.sub(p, "", text, flags=re.IGNORECASE)

    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)

    return text.strip()


def structure_answer(text: str) -> str:
    """
    Делает текст более структурированным: списки, короткие блоки.
    """

    lines = [l.strip() for l in text.split("\n") if l.strip()]

    structured = []
    for line in lines:

        if len(line) > 120:
            structured.append("• " + line)
        else:
            if not (line.startswith("•") or line.startswith("-") or line[0].isdigit()):
                structured.append("• " + line)
            else:
                structured.append(line)

    result = "\n".join(structured)
    return result.strip()


def postprocess_answer(text: str) -> str:
    """
    Финальная обработка.
    """
    cleaned = cleanup_answer(text)
    structured = structure_answer(cleaned)
    return structured
