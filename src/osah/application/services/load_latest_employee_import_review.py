from pathlib import Path

from osah.domain.entities.employee_import_draft import EmployeeImportDraft
from osah.domain.entities.import_batch_summary import ImportBatchSummary
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.get_latest_import_batch_summary import get_latest_import_batch_summary
from osah.infrastructure.database.queries.list_employee_import_drafts_by_batch import list_employee_import_drafts_by_batch


# ###### ЗАВАНТАЖЕННЯ ОСТАННЬОГО ПЕРЕГЛЯДУ ІМПОРТУ / ЗАГРУЗКА ПОСЛЕДНЕГО ПРОСМОТРА ИМПОРТА ######
def load_latest_employee_import_review(
    database_path: Path,
) -> tuple[ImportBatchSummary | None, tuple[EmployeeImportDraft, ...]]:
    """Повертає останню партію імпорту працівників та її чернетки.
    Возвращает последнюю партию импорта сотрудников и её черновики.
    """

    connection = create_database_connection(database_path)
    try:
        latest_batch_summary = get_latest_import_batch_summary(connection)
        if latest_batch_summary is None or latest_batch_summary.entity_scope != "employees":
            return None, ()
        return (
            latest_batch_summary,
            list_employee_import_drafts_by_batch(connection, latest_batch_summary.batch_id),
        )
    finally:
        connection.close()
