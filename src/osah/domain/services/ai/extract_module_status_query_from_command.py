import re

from osah.domain.services.ai.matches_module_status_list_query import matches_module_status_list_query
from osah.domain.services.ai.normalize_ai_module_key import normalize_ai_module_key
from osah.domain.services.ai.normalize_ai_status_filter_key import detect_status_filter_key_from_command

_MODULE_HINTS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("trainings", re.compile(r"\b(?:інструктаж\w*|инструктаж\w*)\b", re.IGNORECASE)),
    ("ppe", re.compile(r"\b(?:зіз|зиз|зі[зс]|сиз|ppe|спецодяг\w*)\b", re.IGNORECASE)),
    ("medical", re.compile(r"\bмед(?:огляд|осмотр)?\w*\b", re.IGNORECASE)),
    ("work_permits", re.compile(r"\bнаряд\w*\b", re.IGNORECASE)),
)


def extract_module_status_query_from_command(raw_command: str) -> tuple[str, str] | None:
    """Витягує module_key і filter_key для спискового запиту за статусом.
    Extracts module_key and filter_key for a module status list query.
    """

    text = raw_command.strip()
    if not matches_module_status_list_query(text):
        return None

    module_key = _detect_module_key(text)
    filter_key = detect_status_filter_key_from_command(text)
    if module_key is None or filter_key is None:
        return None
    return module_key, filter_key


def _detect_module_key(text: str) -> str | None:
    for module_key, pattern in _MODULE_HINTS:
        if pattern.search(text):
            return normalize_ai_module_key(module_key)
    return None
