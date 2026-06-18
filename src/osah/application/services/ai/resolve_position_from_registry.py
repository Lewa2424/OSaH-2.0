from pathlib import Path

from osah.application.services.ai.list_distinct_positions import list_distinct_positions
from osah.application.services.ai.resolve_registry_entity_from_names import resolve_registry_entity_from_names
from osah.domain.entities.registry_entity_resolution import RegistryEntityResolution
from osah.domain.services.ai.match_position_name_query import position_name_matches_query


def resolve_position_from_registry(database_path: Path, position_query: str) -> RegistryEntityResolution:
    """Зіставляє фрагмент посади з реєстром працівників.
    Matches a position query fragment against the employee registry.
    """

    return resolve_registry_entity_from_names(
        position_query,
        tuple(list_distinct_positions(database_path)),
        match_checker=position_name_matches_query,
        token_length=8,
    )
