from dataclasses import dataclass


@dataclass(slots=True)
class AuditLogEntry:
    """Рядок audit-журналу з локальної бази.
    Строка audit-журнала из локальной базы.
    """

    entry_id: int
    event_type: str
    module_name: str
    event_level: str
    actor_name: str
    entity_name: str
    result_status: str
    description_text: str
    created_at_text: str
