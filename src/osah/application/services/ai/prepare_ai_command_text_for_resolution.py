from pathlib import Path

from osah.domain.services.ai.apply_ai_pattern_memory import apply_ai_pattern_memory
from osah.domain.services.ai.normalize_ai_command_text import normalize_ai_command_text


def prepare_ai_command_text_for_resolution(
    command_text: str,
    *,
    database_path: Path | None = None,
) -> tuple[str, str]:
    """Готує текст команди для router/compile: pattern memory → normalize.
    Prepares command text for router/compile: pattern memory → normalize.
    """

    original = command_text.strip()
    prepared = original
    if database_path is not None:
        prepared = apply_ai_pattern_memory(database_path, prepared)
    prepared = normalize_ai_command_text(prepared)
    return original, prepared
