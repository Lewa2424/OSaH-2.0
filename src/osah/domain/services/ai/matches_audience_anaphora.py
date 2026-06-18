import re

_AUDIENCE_ANAPHORA_PATTERN = re.compile(
    r"(?:"
    r"\b(?:им|ім|їм|их|їх|этим|цим|тим)\b|"
    r"\b(?:всем|всім)\s+(?:из|з)\s+списк\w*\b|"
    r"\b(?:из|з)\s+списк\w*\b|"
    r"\b(?:этих|цих|тих)\s+(?:сотрудник|працівник|работник)\w*\b"
    r")",
    re.IGNORECASE,
)


def matches_audience_anaphora(raw_command: str) -> bool:
    """Перевіряє звернення до аудиторії з попередньої відповіді (ім/их/зі списку).
    Checks references to the audience from a previous answer (them/from the list).
    """

    return bool(_AUDIENCE_ANAPHORA_PATTERN.search(raw_command.strip()))
