import re

_MEDICAL_DECISION_ALIASES: dict[str, str] = {
    "fit": "fit",
    "придатний": "fit",
    "годен": "fit",
    "restricted": "restricted",
    "обмеження": "restricted",
    "ограничение": "restricted",
    "not_fit": "not_fit",
    "непридатний": "not_fit",
    "не годен": "not_fit",
}


def normalize_ai_medical_decision(raw_value: str | None, *, default: str = "fit") -> str:
    """Нормалізує медичне рішення з AI-слота.
    Normalizes a medical decision value from an AI slot.
    """

    normalized = re.sub(r"\s+", " ", (raw_value or "").strip().lower())
    if not normalized:
        return default
    if normalized in _MEDICAL_DECISION_ALIASES:
        return _MEDICAL_DECISION_ALIASES[normalized]
    for alias, decision in _MEDICAL_DECISION_ALIASES.items():
        if alias in normalized:
            return decision
    return default
