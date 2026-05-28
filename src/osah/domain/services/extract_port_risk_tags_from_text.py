import re

from osah.domain.services.stem_ukrainian_word import stem_ukrainian_word


_TOKEN_RE = re.compile(r"[a-zA-Zа-яА-ЯіїєґІЇЄҐ0-9]+", re.UNICODE)

_STOPWORDS = frozenset({
    "або",
    "але",
    "без",
    "був",
    "була",
    "було",
    "були",
    "буде",
    "будуть",
    "в",
    "від",
    "внаслідок",
    "виконання",
    "виконанні",
    "для",
    "до",
    "за",
    "з",
    "й",
    "на",
    "над",
    "не",
    "ні",
    "одночасний",
    "одночасної",
    "одночасна",
    "одночасне",
    "під",
    "при",
    "про",
    "роботи",
    "робіт",
    "робота",
    "та",
    "також",
    "тим",
    "тому",
    "того",
    "той",
    "томущо",
    "у",
    "умовах",
    "умова",
    "умови",
    "через",
    "чи",
    "що",
    "який",
    "яка",
    "яке",
    "які",
    "є",
    "і",
    "із",
    "його",
    "її",
    "їх",
    "цей",
    "ця",
    "це",
    "ці",
    "час",
    "часі",
    "наприклад",
    "може",
    "можуть",
    "наявність",
    "відсутність",
    "недостатнє",
    "недостатня",
    "недостатній",
    "раптовий",
    "раптова",
    "раптове",
})


# ###### ВИТЯГ ТЕГІВ З ТЕКСТУ РИЗИКУ / EXTRACT RISK TAGS FROM TEXT ######
def extract_port_risk_tags_from_text(*text_parts: str) -> dict[str, str]:
    """Будує набір тегів (стем -> відображувана форма) з текстових полів ризику.
    Builds a tag set (stem -> display form) from risk text fields.
    """

    tags: dict[str, str] = {}
    for text_part in text_parts:
        if not text_part or not text_part.strip():
            continue
        for segment in _split_segments(text_part):
            _collect_tags_from_segment(segment, tags)
    return tags


def _split_segments(text: str) -> list[str]:
    normalized = " ".join(text.split())
    segments: list[str] = []
    for part in re.split(r"[;,\n]+", normalized):
        cleaned = part.strip()
        if cleaned:
            segments.append(cleaned)
    return segments


def _collect_tags_from_segment(segment: str, tags: dict[str, str]) -> None:
    tokens = _TOKEN_RE.findall(segment.lower())
    stems: list[str] = []
    labels: list[str] = []

    for token in tokens:
        if token in _STOPWORDS:
            continue
        if len(token) < 3 and token not in {"між"}:
            continue
        stem = stem_ukrainian_word(token)
        if not stem or stem in _STOPWORDS or len(stem) < 2:
            continue
        stems.append(stem)
        labels.append(token)
        tags.setdefault(stem, token)

    for index in range(len(stems) - 1):
        bigram_stem = f"{stems[index]} {stems[index + 1]}"
        bigram_label = f"{labels[index]} {labels[index + 1]}"
        tags.setdefault(bigram_stem, bigram_label)

