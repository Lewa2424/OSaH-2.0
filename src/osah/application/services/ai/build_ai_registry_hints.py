import json
from pathlib import Path

from osah.application.services.ai.list_distinct_departments import list_distinct_departments
from osah.application.services.ai.list_distinct_positions import list_distinct_positions

_MAX_HINT_CHARS = 600
_TOP_N = 20


def build_ai_registry_hints(database_path: Path, *, max_chars: int = _MAX_HINT_CHARS) -> str:
    """Повертає компактний JSON з назвами підрозділів і посад із БД для LLM.
    Returns compact JSON of department and position names from the DB for the LLM.
    """

    departments = list(list_distinct_departments(database_path))[:_TOP_N]
    positions = list(list_distinct_positions(database_path))[:_TOP_N]
    payload: dict[str, list[str]] = {"departments": departments, "positions": positions}
    text = json.dumps(payload, ensure_ascii=False)
    while len(text) > max_chars and (departments or positions):
        if len(positions) > len(departments):
            positions.pop()
        elif departments:
            departments.pop()
        else:
            positions.pop()
        payload = {"departments": departments, "positions": positions}
        text = json.dumps(payload, ensure_ascii=False)
    return text
