import re

_POSITION_FROM_PATTERN = re.compile(
    r"(?:"
    r"(?:^|\s)(?:кто|хто|у\s+кого|кому)\s+из\s+"
    r"(?P<from_genitive>[А-Яа-яІіЇїЄєҐґ][А-Яа-яІіЇїЄєҐґa-z\s\-]{2,60})"
    r"|"
    r"(?:^|\s)из\s+"
    r"(?P<from_genitive2>[А-Яа-яІіЇїЄєҐґ][А-Яа-яІіЇїЄєҐґa-z\s\-]{2,60})"
    r"(?:\s+(?:нужда|потреб|нет|не\s+выдан|не\s+видан))"
    r")",
    re.IGNORECASE,
)

_POSITION_DATIVE_PATTERN = re.compile(
    r"\b([А-Яа-яІіЇїЄєҐґ][а-яіїєґa-z]{2,30}(?:альник|ник|щик|ист|ер|ант|ор|ей|ям|ам|ов|ів))\b",
    re.IGNORECASE,
)


def extract_position_span_from_command(raw_command: str) -> str | None:
    """Витягує фрагмент посади з команди (род./дав. відмінок).
    Extracts a position name span from a command phrase.
    """

    text = raw_command.strip()
    if not text:
        return None

    from_match = _POSITION_FROM_PATTERN.search(text)
    if from_match is not None:
        for group_name in ("from_genitive", "from_genitive2"):
            value = from_match.group(group_name)
            if value is not None:
                cleaned = _clean_position_span(value)
                if cleaned:
                    return cleaned

    dative_match = _POSITION_DATIVE_PATTERN.search(text)
    if dative_match is not None:
        cleaned = _clean_position_span(dative_match.group(1))
        if cleaned and not _is_noise_position_token(cleaned):
            return cleaned

    return None


def _clean_position_span(value: str) -> str:
    cleaned = " ".join(value.strip().split())
    cleaned = re.sub(
        r"\s+(?:нужда\w*|потреб\w*|нет|не\s+выдан\w*|не\s+видан\w*|погрузчик\w*).*$",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )
    return cleaned.rstrip("?.!,").strip()


def _is_noise_position_token(value: str) -> bool:
    lowered = value.lower()
    noise = {
        "сотрудник",
        "сотрудников",
        "працівник",
        "працівників",
        "работник",
        "работников",
        "инструктаж",
        "инструктажи",
        "інструктаж",
    }
    return lowered in noise
