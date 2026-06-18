import re

from osah.domain.services.ai.normalize_person_name_token import normalize_person_name_token


def normalize_registry_name_tokens(value: str, *, token_length: int = 6) -> set[str]:
    """Нормалізує текст у множину токенів для fuzzy-зіставлення з реєстром.
    Normalizes text into a token set for fuzzy registry matching.
    """

    normalized = (
        value.strip()
        .lower()
        .replace("ё", "е")
        .replace("э", "е")
        .replace("є", "е")
        .replace("і", "и")
        .replace("ї", "и")
        .replace("ґ", "г")
    )
    tokens = re.findall(r"[а-яa-z0-9]+", normalized)
    return {
        normalize_person_name_token(token)[:token_length]
        for token in tokens
        if len(token) >= 3
    }
