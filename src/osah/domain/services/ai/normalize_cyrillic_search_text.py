def normalize_cyrillic_search_text(text: str) -> str:
    """Нормалізує кирилицю для порівняння RU/UA варіантів написання.
    Normalizes Cyrillic text for RU/UA spelling comparison.
    """

    normalized_chars: list[str] = []
    for char in text.strip().lower():
        if char == "ё":
            normalized_chars.append("є")
        elif char == "ы":
            normalized_chars.append("и")
        elif char == "э":
            normalized_chars.append("е")
        elif char == "и":
            normalized_chars.append("і")
        else:
            normalized_chars.append(char)
    return "".join(normalized_chars)
