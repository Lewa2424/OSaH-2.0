import re

_MARKER_TYPO_RULES: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\bпакажи\b", re.IGNORECASE), "покажи"),
    (re.compile(r"\bпокажы\b", re.IGNORECASE), "покажи"),
    (re.compile(r"\bпаказать\b", re.IGNORECASE), "показать"),
    (re.compile(r"\bпаказати\b", re.IGNORECASE), "показати"),
    (re.compile(r"\bвудай\b", re.IGNORECASE), "выдай"),
    (re.compile(r"\bвыдаи\b", re.IGNORECASE), "выдай"),
    (re.compile(r"\bвидаи\b", re.IGNORECASE), "видай"),
    (re.compile(r"\bдодайь\b", re.IGNORECASE), "додай"),
    (re.compile(r"\bдобавьь\b", re.IGNORECASE), "добавь"),
    (re.compile(r"\bоткройт\b", re.IGNORECASE), "открой"),
    (re.compile(r"\bвідкрийт\b", re.IGNORECASE), "відкрий"),
    (re.compile(r"\bпросроченые\b", re.IGNORECASE), "просроченные"),
    (re.compile(r"\bпрострочени\b", re.IGNORECASE), "прострочені"),
)


def correct_ai_command_marker_typos(command_text: str) -> str:
    """Виправляє типові опечатки в маркерних словах команди.
    Corrects common typos in command marker words.
    """

    normalized = command_text.strip()
    if not normalized:
        return normalized

    for pattern, replacement in _MARKER_TYPO_RULES:
        normalized = pattern.sub(lambda match, rep=replacement: _preserve_case(match.group(0), rep), normalized)
    return normalized


def _preserve_case(source: str, replacement: str) -> str:
    if not source:
        return replacement
    if source[:1].isupper():
        return replacement[:1].upper() + replacement[1:]
    return replacement
