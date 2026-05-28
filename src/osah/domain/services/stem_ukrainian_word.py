"""Стемінг українських слів для зіставлення тегів.
Ukrainian word stemming for tag matching.
"""

_UA_SUFFIXES = (
    "ування",
    "ення",
    "ання",
    "ність",
    "ами",
    "ями",
    "ного",
    "ному",
    "ній",
    "них",
    "ним",
    "ії",
    "ою",
    "ів",
    "ей",
    "ах",
    "ях",
    "ом",
    "ем",
    "ам",
    "ям",
    "ої",
    "ні",
)


# ###### СТЕМ УКРАЇНСЬКОГО СЛОВА / STEM UKRAINIAN WORD ######
def stem_ukrainian_word(word: str) -> str:
    """Повертає основу слова для нечіткого зіставлення форм.
    Returns a word stem for fuzzy form matching.
    """

    normalized = word.lower().strip()
    if len(normalized) <= 2:
        return normalized

    for suffix in _UA_SUFFIXES:
        if len(normalized) > len(suffix) + 3 and normalized.endswith(suffix):
            normalized = normalized[: -len(suffix)]
            break

    if len(normalized) >= 4 and normalized[-1] in "аеиоуяіїює":
        normalized = normalized[:-1]
    if len(normalized) >= 5 and normalized[-1] in "аеиоуяіїює":
        normalized = normalized[:-1]

    return normalized
