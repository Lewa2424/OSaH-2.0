from osah.domain.services.ai.correct_ai_command_marker_typos import correct_ai_command_marker_typos
from osah.domain.services.ai.normalize_ai_command_synonyms import normalize_ai_command_synonyms


def normalize_ai_command_text(command_text: str) -> str:
    """Підготовлює текст команди: синоніми, потім виправлення опечаток маркерів.
    Prepares command text: synonyms first, then marker typo corrections.
    """

    normalized = command_text.strip()
    if not normalized:
        return normalized

    normalized = normalize_ai_command_synonyms(normalized)
    normalized = correct_ai_command_marker_typos(normalized)
    return normalized
