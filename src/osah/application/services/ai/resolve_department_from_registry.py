from pathlib import Path

from osah.application.services.ai.list_distinct_departments import list_distinct_departments
from osah.application.services.ai.resolve_registry_entity_from_names import resolve_registry_entity_from_names
from osah.domain.entities.registry_entity_resolution import RegistryEntityResolution
from osah.domain.services.ai.match_department_name_query import department_name_matches_query


def resolve_department_from_registry(database_path: Path, department_query: str) -> RegistryEntityResolution:
    """Зіставляє фрагмент підрозділу з реєстром працівників.
    Matches a department query fragment against the employee registry.
    """

    return resolve_registry_entity_from_names(
        department_query,
        tuple(list_distinct_departments(database_path)),
        match_checker=department_name_matches_query,
        token_length=6,
    )
