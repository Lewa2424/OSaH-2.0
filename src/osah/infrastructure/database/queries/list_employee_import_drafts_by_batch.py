from sqlite3 import Connection

from osah.domain.entities.employee_import_draft import EmployeeImportDraft
from osah.domain.entities.employee_import_draft_status import EmployeeImportDraftStatus


# ###### ЧИТАННЯ ЧЕРНЕТОК ІМПОРТУ ПРАЦІВНИКІВ / ЧТЕНИЕ ЧЕРНОВИКОВ ИМПОРТА СОТРУДНИКОВ ######
def list_employee_import_drafts_by_batch(connection: Connection, batch_id: int) -> tuple[EmployeeImportDraft, ...]:
    """Повертає чернетки імпорту працівників для обраної партії.
    Возвращает черновики импорта сотрудников для выбранной партии.
    """

    rows = connection.execute(
        """
        SELECT
            id,
            batch_id,
            source_row_number,
            personnel_number,
            full_name,
            position_name,
            department_name,
            employment_status,
            resolution_status,
            issue_text
        FROM employee_import_drafts
        WHERE batch_id = ?
        ORDER BY source_row_number ASC, id ASC;
        """,
        (batch_id,),
    ).fetchall()
    return tuple(
        EmployeeImportDraft(
            draft_id=int(row["id"]),
            batch_id=int(row["batch_id"]),
            source_row_number=int(row["source_row_number"]),
            personnel_number=row["personnel_number"],
            full_name=row["full_name"],
            position_name=row["position_name"],
            department_name=row["department_name"],
            employment_status=row["employment_status"],
            resolution_status=EmployeeImportDraftStatus(row["resolution_status"]),
            issue_text=row["issue_text"] or "",
        )
        for row in rows
    )
