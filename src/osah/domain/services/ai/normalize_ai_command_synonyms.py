import re

_LEADING_SYNONYM_RULES: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"^\s*отобрази(?:ть)?\b", re.IGNORECASE), "покажи"),
    (re.compile(r"^\s*показать\b", re.IGNORECASE), "покажи"),
    (re.compile(r"^\s*перечисли(?:ть)?\b", re.IGNORECASE), "покажи"),
)

_WORD_SYNONYM_RULES: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\bотобрази(?:ть)?\b", re.IGNORECASE), "покажи"),
    (re.compile(r"\bподраздлени(?:е|я|ю|ем|и)\b", re.IGNORECASE), "подразделение"),
    (re.compile(r"\bпідроздлени(?:я|ю|і|ів)\b", re.IGNORECASE), "підрозділ"),
)


def normalize_ai_command_synonyms(command_text: str) -> str:
    """Нормалізує синоніми дієслів і службових маркерів у тексті команди.
    Normalizes verb and marker synonyms in command text.
    """

    normalized = command_text.strip()
    if not normalized:
        return normalized

    for pattern, replacement in _LEADING_SYNONYM_RULES:
        normalized = pattern.sub(replacement, normalized, count=1)
    for pattern, replacement in _WORD_SYNONYM_RULES:
        normalized = pattern.sub(replacement, normalized)
    return normalized
