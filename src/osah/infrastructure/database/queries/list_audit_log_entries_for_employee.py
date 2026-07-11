from sqlite3 import Connection

from osah.domain.entities.audit_log_entry import AuditLogEntry
from osah.domain.entities.employee_audit_entity_keys import EmployeeAuditEntityKeys


# ###### AUDIT-ЖУРНАЛ ПРАЦІВНИКА / LIST AUDIT LOG ENTRIES FOR EMPLOYEE ######
def list_audit_log_entries_for_employee(
    connection: Connection,
    entity_keys: EmployeeAuditEntityKeys,
    *,
    limit: int = 100,
) -> tuple[AuditLogEntry, ...]:
    """Повертає audit-події, пов'язані з працівником, у зворотному хронологічному порядку.
    Returns employee-related audit events in reverse chronological order.
    """

    normalized_limit = min(max(limit, 1), 500)
    exact_keys = tuple(sorted(entity_keys.exact_entity_names))
    training_like_pattern = f"{entity_keys.training_entity_prefix}%"
    legacy_personnel_entity_name = entity_keys.legacy_personnel_entity_name

    if exact_keys:
        placeholders = ",".join("?" for _ in exact_keys)
        where_clause = f"""
            entity_name IN ({placeholders})
            OR entity_name LIKE ?
            OR entity_name = ?
        """
        parameters: tuple[object, ...] = (
            *exact_keys,
            training_like_pattern,
            legacy_personnel_entity_name,
            normalized_limit,
        )
    else:
        where_clause = """
            entity_name LIKE ?
            OR entity_name = ?
        """
        parameters = (
            training_like_pattern,
            legacy_personnel_entity_name,
            normalized_limit,
        )

    rows = connection.execute(
        f"""
        SELECT
            id,
            event_type,
            module_name,
            event_level,
            actor_name,
            entity_name,
            result_status,
            description_text,
            created_at
        FROM audit_log
        WHERE {where_clause}
        ORDER BY id DESC
        LIMIT ?;
        """,
        parameters,
    ).fetchall()

    return tuple(
        AuditLogEntry(
            entry_id=int(row["id"]),
            event_type=row["event_type"],
            module_name=row["module_name"],
            event_level=row["event_level"],
            actor_name=row["actor_name"],
            entity_name=row["entity_name"],
            result_status=row["result_status"],
            description_text=row["description_text"],
            created_at_text=row["created_at"],
        )
        for row in rows
    )
