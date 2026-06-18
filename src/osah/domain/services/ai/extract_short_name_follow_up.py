import re

_SHORT_NAME_FOLLOW_UP_PATTERN = re.compile(
    r"^\s*(?:а|і)\s+"
    r"([А-Яа-яІіЇїЄєҐґ][а-яіїєґ'`-]{2,40}(?:у|ю|а|е|и|і)?)"
    r"\s*[?.!]?\s*$",
    re.IGNORECASE,
)


def extract_short_name_follow_up(raw_command: str) -> str | None:
    """Витягує ім'я з короткого follow-up на кшталт «а Іванову?».
    Extracts a name from a short follow-up like 'а Ivanovu?'.
    """

    match = _SHORT_NAME_FOLLOW_UP_PATTERN.match(raw_command.strip())
    if match is None:
        return None
    return match.group(1).strip().rstrip("?.!,")
