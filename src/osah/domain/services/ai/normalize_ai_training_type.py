import re

_TRAINING_TYPE_ALIASES: dict[str, str] = {
    "introductory": "introductory",
    "вступний": "introductory",
    "вводный": "introductory",
    "primary": "primary",
    "первинний": "primary",
    "первичный": "primary",
    "repeated": "repeated",
    "повторний": "repeated",
    "повторный": "repeated",
    "targeted": "targeted",
    "цільовий": "targeted",
    "целевой": "targeted",
    "unscheduled": "unscheduled",
    "позаплановий": "unscheduled",
    "внеплановый": "unscheduled",
}


def normalize_ai_training_type(raw_value: str | None, *, default: str = "repeated") -> str:
    """Нормалізує тип інструктажу з AI-слота.
    Normalizes a training type value from an AI slot.
    """

    normalized = re.sub(r"\s+", " ", (raw_value or "").strip().lower())
    if not normalized:
        return default
    if normalized in _TRAINING_TYPE_ALIASES:
        return _TRAINING_TYPE_ALIASES[normalized]
    for alias, training_type in _TRAINING_TYPE_ALIASES.items():
        if alias in normalized:
            return training_type
    return default


def infer_ai_training_type_from_command(raw_command: str) -> str | None:
    """Визначає тип інструктажу з тексту команди, якщо він згаданий.
    Infers a training type from command text when it is mentioned.
    """

    normalized = re.sub(r"\s+", " ", raw_command.strip().lower())
    if not normalized:
        return None
    if normalized in _TRAINING_TYPE_ALIASES:
        return _TRAINING_TYPE_ALIASES[normalized]
    for alias, training_type in _TRAINING_TYPE_ALIASES.items():
        if alias in normalized:
            return training_type
    return None
