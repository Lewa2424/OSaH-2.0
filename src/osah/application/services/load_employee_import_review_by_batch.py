from pathlib import Path

from osah.domain.entities.employee_import_draft import EmployeeImportDraft
from osah.domain.entities.import_batch_summary import ImportBatchSummary
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.get_import_batch_summary_by_id import get_import_batch_summary_by_id
from osah.infrastructure.database.queries.list_employee_import_drafts_by_batch import list_employee_import_drafts_by_batch


# ###### ЗАВАНТАЖЕННЯ ПЕРЕГЛЯДУ ПАРТІЇ ІМПОРТУ ЗА ID / LOAD IMPORT BATCH REVIEW BY ID ######
def load_employee_import_review_by_batch(
    database_path: Path,
    batch_id: int,
) -> tuple[ImportBatchSummary | None, tuple[EmployeeImportDraft, ...]]:
    """Повертає підсумок конкретної партії імпорту працівників та її чернетки.
    Returns a specific employee import batch summary and its drafts.
    """

    connection = create_database_connection(database_path)
    try:
        batch_summary = get_import_batch_summary_by_id(connection, batch_id)
        if batch_summary is None or batch_summary.entity_scope != "employees":
            return None, ()
        return batch_summary, list_employee_import_drafts_by_batch(connection, batch_id)
    finally:
        connection.close()
