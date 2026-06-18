from pathlib import Path

from osah.application.services.load_ppe_registry import load_ppe_registry
from osah.domain.services.ai.normalize_ppe_item_query import normalize_ppe_item_query
from osah.domain.services.ai.resolve_ppe_item_alias import resolve_ppe_item_alias
from osah.domain.services.ai.suggest_registry_name_candidates import suggest_registry_name_candidates
from osah.domain.services.build_default_ppe_names import build_default_ppe_names


def search_ppe_catalog_candidates(
    database_path: Path,
    item_name: str,
    *,
    limit: int = 5,
) -> tuple[str, ...]:
    """Повертає кандидатів назв ЗІЗ за нечітким запитом.
    Returns PPE name candidates for a fuzzy item query.
    """

    normalized_item = normalize_ppe_item_query(item_name).lower()
    if not normalized_item:
        return ()

    known_names = {record.ppe_name.strip() for record in load_ppe_registry(database_path) if record.ppe_name.strip()}
    if not known_names:
        known_names = set(build_default_ppe_names())

    search_tokens = [normalized_item]
    alias_name = resolve_ppe_item_alias(normalize_ppe_item_query(item_name))
    if alias_name:
        search_tokens.append(alias_name.strip().lower())

    substring_matches = sorted(
        {
            known_name
            for known_name in known_names
            for token in search_tokens
            if token in known_name.lower() or known_name.lower() in token
        },
        key=len,
    )
    if substring_matches:
        return tuple(substring_matches[:limit])

    return suggest_registry_name_candidates(
        normalized_item,
        tuple(sorted(known_names)),
        limit=limit,
        min_score=0.34,
        token_length=6,
    )
