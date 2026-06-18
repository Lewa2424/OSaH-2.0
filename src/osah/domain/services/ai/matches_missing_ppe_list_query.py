import re

from osah.domain.services.ai.detect_ai_command_track import extract_ppe_token_from_command

_LIST_LEAD_PATTERN = re.compile(
    r"(?:^|\s)(?:кому|у\s+кого|хто)\b",
    re.IGNORECASE,
)
_MISSING_PPE_NEGATION_PATTERN = re.compile(
    r"(?:"
    r"нет|немає|нема|отсутств|без|"
    r"не\s+(?:видан\w*|выдан\w*)|"
    r"(?:не\s+)?(?:видали|выдали)|"
    r"потрібн\w*|нужн\w*"
    r")",
    re.IGNORECASE,
)


def matches_missing_ppe_list_query(raw_command: str) -> bool:
    """Перевіряє запит списку працівників без видачі ЗІЗ.
    Checks whether the phrase asks for employees missing a PPE item.
    """

    text = raw_command.strip()
    if not text:
        return False
    if not _LIST_LEAD_PATTERN.search(text):
        return False
    if extract_ppe_token_from_command(text) is None:
        return False
    return _MISSING_PPE_NEGATION_PATTERN.search(text) is not None
