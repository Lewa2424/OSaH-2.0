from pathlib import Path

from osah.application.services.security.ensure_write_access import ensure_write_access
from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.employee_import_draft import EmployeeImportDraft
from osah.domain.services.http_fetch_limits import MAX_EMPLOYEE_IMPORT_FILE_BYTES, MAX_EMPLOYEE_IMPORT_ROWS
from osah.domain.entities.employee_import_draft_status import EmployeeImportDraftStatus
from osah.domain.services.build_employee_import_draft import build_employee_import_draft
from osah.infrastructure.database.commands.insert_audit_log import insert_audit_log
from osah.infrastructure.database.commands.insert_employee_import_draft import insert_employee_import_draft
from osah.infrastructure.database.commands.insert_import_batch import insert_import_batch
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.list_employees import list_employees
from osah.infrastructure.importing.read_employee_rows_from_json_file import read_employee_rows_from_json_file
from osah.infrastructure.importing.read_employee_rows_from_xlsx_file import read_employee_rows_from_xlsx_file


# ###### СТВОРЕННЯ ПАРТІЇ ЧЕРНЕТОК ІМПОРТУ / СОЗДАНИЕ ПАРТИИ ЧЕРНОВИКОВ ИМПОРТА ######
def create_employee_import_batch_from_file(
    database_path: Path,
    source_path: Path,
    *,
    access_role: AccessRole,
) -> int:
    """Створює партію чернеток імпорту працівників з підтриманого файлу.
    Создаёт партию черновиков импорта сотрудников из поддерживаемого файла.
    """

    ensure_write_access(access_role, "create_employee_import_batch_from_file")
    if not source_path.exists():
        raise ValueError("Файл імпорту не знайдено.")
    file_size_bytes = source_path.stat().st_size
    if file_size_bytes > MAX_EMPLOYEE_IMPORT_FILE_BYTES:
        raise ValueError(
            f"Файл імпорту перевищує ліміт {MAX_EMPLOYEE_IMPORT_FILE_BYTES // (1024 * 1024)} МБ."
        )
    source_format = source_path.suffix.strip().lower()
    row_data = _read_employee_import_rows(source_path, source_format)
    if len(row_data) > MAX_EMPLOYEE_IMPORT_ROWS:
        raise ValueError(f"Файл імпорту містить понад {MAX_EMPLOYEE_IMPORT_ROWS} рядків.")

    connection = create_database_connection(database_path)
    try:
        existing_employees = list_employees(connection)
        existing_employees_by_number = {
            employee.personnel_number: employee
            for employee in existing_employees
        }

        draft_blueprints: list[EmployeeImportDraft] = []
        for row_index, import_row in enumerate(row_data, start=2):
            draft_blueprints.append(
                build_employee_import_draft(
                    batch_id=0,
                    source_row_number=row_index,
                    row_data=import_row,
                    existing_employees_by_number=existing_employees_by_number,
                )
            )

        valid_total = sum(
            1
            for draft_blueprint in draft_blueprints
            if draft_blueprint.resolution_status != EmployeeImportDraftStatus.INVALID
        )
        invalid_total = len(draft_blueprints) - valid_total
        batch_id = insert_import_batch(
            connection,
            source_name=source_path.name,
            source_format=source_format.removeprefix("."),
            entity_scope="employees",
            draft_total=len(draft_blueprints),
            valid_total=valid_total,
            invalid_total=invalid_total,
        )
        for draft_blueprint in draft_blueprints:
            insert_employee_import_draft(
                connection,
                EmployeeImportDraft(
                    draft_id=None,
                    batch_id=batch_id,
                    source_row_number=draft_blueprint.source_row_number,
                    personnel_number=draft_blueprint.personnel_number,
                    full_name=draft_blueprint.full_name,
                    position_name=draft_blueprint.position_name,
                    department_name=draft_blueprint.department_name,
                    employment_status=draft_blueprint.employment_status,
                    resolution_status=draft_blueprint.resolution_status,
                    issue_text=draft_blueprint.issue_text,
                ),
            )
        insert_audit_log(
            connection,
            event_type="import.drafts_created",
            module_name="import_export",
            event_level="info",
            actor_name="system",
            entity_name=f"batch:{batch_id}",
            result_status="success",
            description_text=f"source={source_path.name};draft_total={len(draft_blueprints)};invalid_total={invalid_total}",
        )
        connection.commit()
        return batch_id
    finally:
        connection.close()


# ###### ЧИТАННЯ РЯДКІВ ІМПОРТУ ПРАЦІВНИКІВ / ЧТЕНИЕ СТРОК ИМПОРТА СОТРУДНИКОВ ######
def _read_employee_import_rows(source_path: Path, source_format: str) -> tuple[dict[str, str], ...]:
    """Повертає нормалізовані рядки працівників з підтриманого формату.
    Возвращает нормализованные строки сотрудников из поддерживаемого формата.
    """

    if source_format == ".json":
        return read_employee_rows_from_json_file(source_path)
    if source_format == ".xlsx":
        return read_employee_rows_from_xlsx_file(source_path)
    raise ValueError("Підтримуються лише файли JSON та XLSX.")
