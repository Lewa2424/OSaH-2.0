from osah.domain.services.ai.normalize_cyrillic_search_text import normalize_cyrillic_search_text

_NAME_STEM_ENDINGS = ("ей", "ий", "ій", "ею", "ию", "ію")


def normalize_person_name_token(token: str) -> str:
    """Зводить RU/UA варіанти імені до спільного стему для зіставлення.
    Converges RU/UA name token spellings to a shared stem for matching.
    """

    cleaned = token.strip()
    if not cleaned:
        return ""

    lowered = cleaned.lower()
    for ending in _NAME_STEM_ENDINGS:
        if len(cleaned) > len(ending) + 1 and lowered.endswith(ending):
            return normalize_cyrillic_search_text(cleaned[: -len(ending)])

    if len(cleaned) > 3 and lowered.endswith("у"):
        return normalize_cyrillic_search_text(cleaned[:-1])
    if len(cleaned) > 3 and lowered.endswith("ю"):
        return normalize_cyrillic_search_text(cleaned[:-1])
    if len(cleaned) > 3 and lowered.endswith("е"):
        return normalize_cyrillic_search_text(cleaned[:-1])

    return normalize_cyrillic_search_text(cleaned)
