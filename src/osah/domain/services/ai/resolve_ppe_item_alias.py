_PPE_ITEM_ALIASES: dict[str, str] = {
    "взуття": "Черевики захисні",
    "взутт": "Черевики захисні",
    "обув": "Черевики захисні",
    "ботинк": "Черевики захисні",
    "ботинок": "Черевики захисні",
    "черевик": "Черевики захисні",
    "каск": "Каска захисна",
    "каску": "Каска захисна",
    "каски": "Каска захисна",
    "касок": "Каска захисна",
    "рукавиц": "Рукавиці захисні",
    "перчат": "Рукавиці захисні",
    "перчаток": "Рукавиці захисні",
    "жилет": "Жилет сигнальний",
    "комбінезон": "Комбінезон захисний",
}


def resolve_ppe_item_alias(item_query: str) -> str | None:
    """Повертає канонічну назву ЗІЗ для короткого псевдоніма.
    Returns a canonical PPE name for a short alias token.
    """

    normalized = item_query.strip().lower()
    if not normalized:
        return None
    if normalized in _PPE_ITEM_ALIASES:
        return _PPE_ITEM_ALIASES[normalized]
    for alias, canonical_name in _PPE_ITEM_ALIASES.items():
        if alias in normalized:
            return canonical_name
    return None
