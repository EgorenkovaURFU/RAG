import re


CLEAN_PATTERNS = [
    r"как модель[^.]+\.?",
    r"как ассистент[^.]+\.?",
    r"я основан на модели[^.]+\.?",
    r"исходя из предоставленного контекста[:, ]*",
    r"в предоставленном контексте[:, ]*",
    r"на основе контекста[:, ]*",
    r"привет[^.!\n]+[\n.!]?",
    r"я могу помочь[^.]+\.?",
    r"вот ответ на ваш вопрос[:, ]*",
    r"ниже приведен ответ[:, ]*",
]


def cleanup_answer(text: str) -> str:
    for p in CLEAN_PATTERNS:
        text = re.sub(p, "", text, flags=re.IGNORECASE)

    text = text.replace("**", "")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


SECTION_KEYWORDS = {
    "назначение": ["назначение", "описание", "суть", "что это"],
    "требования": ["требования", "условия", "необходимо", "должен"],
    "порядок": ["порядок", "шаги", "выполнение", "монтаж", "демонтаж"],
    "особенности": ["особенности", "важно", "учитывать"],
    "безопасность": ["безопас", "предосторож", "охрана труда"],
    "примечания": ["примечан", "дополнительно", "замечания"],
}


def detect_section(line: str):
    l = line.lower()
    for sec, keys in SECTION_KEYWORDS.items():
        for k in keys:
            if k in l:
                return sec
    return None


def structure_answer(text: str) -> str:
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    sections = {
        "назначение": [],
        "требования": [],
        "порядок": [],
        "особенности": [],
        "безопасность": [],
        "примечания": [],
    }

    current = None

    for line in lines:
        sec = detect_section(line)
        if sec:
            current = sec
            continue

        if current is None:
            current = "назначение"

        if len(line) > 120:
            sections[current].append("• " + line)
        else:
            if not (line.startswith("•") or line.startswith("-") or line[0].isdigit()):
                sections[current].append("• " + line)
            else:
                sections[current].append(line)

    out = []
    for sec, items in sections.items():
        if items:
            title = sec.capitalize()
            out.append(f"\n### {title}\n" + "\n".join(items))

    return "\n".join(out).strip()


def postprocess_answer(text: str) -> str:
    cleaned = cleanup_answer(text)
    structured = structure_answer(cleaned)
    return structured
