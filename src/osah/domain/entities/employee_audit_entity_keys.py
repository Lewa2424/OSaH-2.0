from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class EmployeeAuditEntityKeys:
    """Ключі audit-журналу для фільтрації історії працівника.
    Audit journal keys used to filter an employee history.
    """

    exact_entity_names: frozenset[str]
    training_entity_prefix: str
    legacy_personnel_entity_name: str
