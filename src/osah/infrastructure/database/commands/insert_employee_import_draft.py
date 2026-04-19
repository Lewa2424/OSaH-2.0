from sqlite3 import Connection

from osah.domain.entities.employee_import_draft import EmployeeImportDraft


# ###### ДОДАВАННЯ ЧЕРНЕТКИ ІМПОРТУ ПРАЦІВНИКА / ДОБАВЛЕНИЕ ЧЕРНОВИКА ИМПОРТА СОТРУДНИКА ######
def insert_employee_import_draft(connection: Connection, employee_import_draft: EmployeeImportDraft) -> None:
    """Зберігає чернетку імпорту працівника у локальній базі.
    Сохраняет черновик импорта сотрудника в локальной базе.
    """

    connection.execute(
        """
        INSERT INTO employee_import_drafts (
            batch_id,
            source_row_number,
            personnel_number,
            full_name,
            position_name,
            department_name,
            employment_status,
            resolution_status,
            issue_text
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
        (
            employee_import_draft.batch_id,
            employee_import_draft.source_row_number,
            employee_import_draft.personnel_number,
            employee_import_draft.full_name,
            employee_import_draft.position_name,
            employee_import_draft.department_name,
            employee_import_draft.employment_status,
            employee_import_draft.resolution_status.value,
            employee_import_draft.issue_text,
        ),
    )
