import re

from osah.domain.services.ai.registry_tokens_typo_match import query_tokens_match_registry_name


def position_name_matches_query(position_name: str, position_query: str) -> bool:
    """Перевіряє, чи посада відповідає фрагменту запиту.
    Checks whether a position name matches a query fragment.
    """

    name = position_name.strip().lower()
    query = position_query.strip().lower()
    if not name or not query:
        return False
    if query in name or name in query:
        return True

    name_tokens = _normalize_position_tokens(name)
    query_tokens = _normalize_position_tokens(query)
    if not name_tokens or not query_tokens:
        return False
    if query_tokens.issubset(name_tokens) or name_tokens.issubset(query_tokens):
        return True
    return query_tokens_match_registry_name(query_tokens, name_tokens)


def _normalize_position_tokens(value: str) -> set[str]:
    normalized = (
        value.lower()
        .replace("ё", "е")
        .replace("э", "е")
        .replace("є", "е")
        .replace("і", "и")
        .replace("ї", "и")
        .replace("ґ", "г")
    )
    tokens = re.findall(r"[а-яa-z0-9]+", normalized)
    return {token[:8] for token in tokens if len(token) >= 3}
