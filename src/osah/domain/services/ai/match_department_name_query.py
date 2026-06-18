import re

from osah.domain.services.ai.registry_tokens_typo_match import query_tokens_match_registry_name


def department_name_matches_query(department_name: str, department_query: str) -> bool:
    """Перевіряє, чи назва підрозділу відповідає фрагменту запиту.
    Checks whether a department name matches a query fragment.
    """

    name = department_name.strip().lower()
    query = department_query.strip().lower()
    if not name or not query:
        return False
    if query in name or name in query:
        return True
    if _matches_occupational_safety_department(name, query):
        return True

    name_tokens = _normalize_department_tokens(name)
    query_tokens = _normalize_department_tokens(query)
    if not name_tokens or not query_tokens:
        return False
    if query_tokens.issubset(name_tokens) or name_tokens.issubset(query_tokens):
        return True
    if _semantic_department_roots_match(query_tokens, name_tokens):
        return True
    return query_tokens_match_registry_name(query_tokens, name_tokens)


def _semantic_department_roots_match(query_tokens: set[str], name_tokens: set[str]) -> bool:
    """Звіряє RU/UK корені (свар/звар + участ/дільниця/цех).
    Matches RU/UK department roots (weld + area/section).
    """

    query_roots = _semantic_department_roots(query_tokens)
    name_roots = _semantic_department_roots(name_tokens)
    if len(query_roots) < 2 or len(name_roots) < 2:
        return False
    return query_roots.issubset(name_roots) or name_roots.issubset(query_roots)


def _semantic_department_roots(tokens: set[str]) -> set[str]:
    roots: set[str] = set()
    for token in tokens:
        if token.startswith(("свар", "звар")):
            roots.add("weld")
            continue
        if token.startswith(("учас", "участ", "дильн", "дільн", "цех")):
            roots.add("area")
            continue
        roots.add(token)
    return roots


def _matches_occupational_safety_department(name: str, query: str) -> bool:
    ot_name = re.search(r"(?:охорон\w*|охран\w*).{0,20}(?:прац\w*|труд\w*)", name, re.IGNORECASE)
    ot_query = re.search(r"(?:охорон\w*|охран\w*).{0,20}(?:прац\w*|труд\w*)", query, re.IGNORECASE)
    return ot_name is not None and ot_query is not None


def _normalize_department_tokens(value: str) -> set[str]:
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
    return {token[:6] for token in tokens if len(token) >= 3}
