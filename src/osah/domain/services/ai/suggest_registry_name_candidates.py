from collections.abc import Callable

from osah.domain.services.ai.score_registry_name_similarity import score_registry_name_similarity


def suggest_registry_name_candidates(
    query: str,
    registry_names: tuple[str, ...] | list[str],
    *,
    exact_match_checker: Callable[[str, str], bool] | None = None,
    limit: int = 5,
    min_score: float = 0.35,
    token_length: int = 6,
) -> tuple[str, ...]:
    """Повертає найближчі назви з реєстру для режиму уточнення.
    Returns the closest registry names for clarification mode.
    """

    normalized_query = query.strip()
    if not normalized_query:
        return ()

    scored: list[tuple[float, str]] = []
    seen: set[str] = set()
    for registry_name in registry_names:
        candidate = registry_name.strip()
        if not candidate:
            continue
        key = candidate.lower()
        if key in seen:
            continue
        seen.add(key)
        score = score_registry_name_similarity(
            normalized_query,
            candidate,
            exact_match_checker=exact_match_checker,
            token_length=token_length,
        )
        if score >= min_score:
            scored.append((score, candidate))

    scored.sort(key=lambda item: (-item[0], len(item[1]), item[1].lower()))
    return tuple(name for _score, name in scored[:limit])
