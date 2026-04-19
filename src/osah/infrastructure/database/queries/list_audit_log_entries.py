from sqlite3 import Connection

from osah.domain.entities.audit_log_entry import AuditLogEntry


# ###### ЧИТАННЯ AUDIT-ЖУРНАЛУ / ЧТЕНИЕ AUDIT-ЖУРНАЛА ######
def list_audit_log_entries(connection: Connection, limit: int = 20) -> tuple[AuditLogEntry, ...]:
    """Повертає останні записи audit-журналу у зворотному хронологічному порядку.
    Возвращает последние записи audit-журнала в обратном хронологическом порядке.
    """

    rows = connection.execute(
        """
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
        ORDER BY id DESC
        LIMIT ?;
        """,
        (limit,),
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
