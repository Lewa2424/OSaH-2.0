import re

_PRONOUN_PATTERN = re.compile(
    r"\b(?:ему|ей|єй|їй|его|її|йому|нему|неё|неї)\b",
    re.IGNORECASE,
)


def matches_audience_pronoun(raw_command: str) -> bool:
    """Перевіряє займенникове посилання на останнього згаданого працівника.
    Checks pronominal reference to the last mentioned employee.
    """

    return bool(_PRONOUN_PATTERN.search(raw_command.strip()))
