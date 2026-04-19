from pathlib import Path

from osah.domain.entities.audit_log_entry import AuditLogEntry
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.list_audit_log_entries import list_audit_log_entries


# ###### ЗАВАНТАЖЕННЯ AUDIT-ЖУРНАЛУ / ЗАГРУЗКА AUDIT-ЖУРНАЛА ######
def load_audit_log_entries(database_path: Path, limit: int = 20) -> tuple[AuditLogEntry, ...]:
    """Повертає останні записи audit-журналу з локальної бази.
    Возвращает последние записи audit-журнала из локальной базы.
    """

    connection = create_database_connection(database_path)
    try:
        return list_audit_log_entries(connection, limit=limit)
    finally:
        connection.close()
