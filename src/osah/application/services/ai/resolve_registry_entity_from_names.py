from collections.abc import Callable

from osah.domain.entities.registry_entity_resolution import RegistryEntityResolution
from osah.domain.services.ai.suggest_registry_name_candidates import suggest_registry_name_candidates


def _normalized_registry_label(value: str) -> str:
    return (
        value.strip()
        .lower()
        .replace("ё", "е")
        .replace("э", "е")
        .replace("є", "е")
        .replace("і", "и")
        .replace("ї", "и")
        .replace("ґ", "г")
    )


def resolve_registry_entity_from_names(
    query: str,
    registry_names: tuple[str, ...],
    *,
    match_checker: Callable[[str, str], bool],
    token_length: int = 6,
    suggestion_limit: int = 5,
    suggestion_min_score: float = 0.35,
) -> RegistryEntityResolution:
    """Зіставляє фрагмент запиту зі списком назв реєстру та пропонує близькі варіанти.
    Matches a query fragment against registry names and suggests close alternatives.
    """

    normalized_query = query.strip()
    if not normalized_query:
        return RegistryEntityResolution(status="empty")

    normalized_query_key = _normalized_registry_label(normalized_query)
    exact_matches = tuple(
        name
        for name in registry_names
        if _normalized_registry_label(name) == normalized_query_key
    )
    if len(exact_matches) == 1:
        return RegistryEntityResolution(status="resolved", canonical_name=exact_matches[0])
    if len(exact_matches) > 1:
        return RegistryEntityResolution(status="ambiguous", candidates=exact_matches)

    matches = tuple(name for name in registry_names if match_checker(name, normalized_query))
    if not matches:
        suggestions = suggest_registry_name_candidates(
            normalized_query,
            registry_names,
            exact_match_checker=match_checker,
            limit=suggestion_limit,
            min_score=suggestion_min_score,
            token_length=token_length,
        )
        if suggestions:
            return RegistryEntityResolution(status="suggest", candidates=suggestions)
        return RegistryEntityResolution(status="not_found")
    if len(matches) == 1:
        return RegistryEntityResolution(status="resolved", canonical_name=matches[0])
    return RegistryEntityResolution(status="ambiguous", candidates=matches)
