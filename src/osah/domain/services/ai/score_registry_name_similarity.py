from collections.abc import Callable

from osah.domain.services.ai.normalize_registry_name_tokens import normalize_registry_name_tokens
from osah.domain.services.ai.registry_tokens_typo_match import registry_tokens_typo_match


def score_registry_name_similarity(
    query: str,
    registry_name: str,
    *,
    exact_match_checker: Callable[[str, str], bool] | None = None,
    token_length: int = 6,
) -> float:
    """Оцінює схожість запиту з назвою з реєстру (0..1).
    Scores similarity between a query fragment and a registry name (0..1).
    """

    normalized_query = query.strip().lower()
    normalized_name = registry_name.strip().lower()
    if not normalized_query or not normalized_name:
        return 0.0
    if normalized_query == normalized_name:
        return 1.0
    if exact_match_checker is not None and exact_match_checker(registry_name, query):
        return 1.0
    if normalized_query in normalized_name or normalized_name in normalized_query:
        return 0.92

    query_tokens = normalize_registry_name_tokens(normalized_query, token_length=token_length)
    name_tokens = normalize_registry_name_tokens(normalized_name, token_length=token_length)
    if not query_tokens or not name_tokens:
        return 0.0

    if query_tokens.issubset(name_tokens) or name_tokens.issubset(query_tokens):
        return 0.88

    intersection = query_tokens & name_tokens
    union = query_tokens | name_tokens
    jaccard = len(intersection) / len(union) if union else 0.0

    matched_query_tokens = sum(
        1
        for query_token in query_tokens
        if any(registry_tokens_typo_match(query_token, name_token) for name_token in name_tokens)
    )
    typo_ratio = matched_query_tokens / len(query_tokens)

    prefix_bonus = 0.0
    for query_token in query_tokens:
        for name_token in name_tokens:
            if query_token[:4] and name_token[:4] and query_token[:4] == name_token[:4]:
                prefix_bonus = max(prefix_bonus, 0.45)
                break

    return max(jaccard, typo_ratio * 0.84, prefix_bonus)
