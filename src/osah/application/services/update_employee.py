from pathlib import Path
import shutil

from osah.domain.entities.employee import Employee
from osah.infrastructure.database.commands.insert_audit_log import insert_audit_log
from osah.infrastructure.database.commands.upsert_employee_row import upsert_employee_row
from osah.infrastructure.database.create_database_connection import create_database_connection


# ###### ОНОВЛЕННЯ ПРАЦІВНИКА / UPDATE EMPLOYEE ######
def update_employee(
    database_path: Path,
    personnel_number: str,
    full_name: str,
    department_name: str,
    position_name: str,
    employment_status: str,
    source_photo_path: str | None = None,
    remove_photo: bool = False,
) -> None:
    """Оновлює існуючого працівника з базовою валідацією та audit-логом.
    Updates an existing employee with basic validation and audit log.
    """

    normalized_personnel_number = personnel_number.strip()
    normalized_full_name = full_name.strip()
    normalized_department_name = department_name.strip()
    normalized_position_name = position_name.strip()
    normalized_status = employment_status.strip().lower() or "active"

    if not normalized_personnel_number:
        raise ValueError("Потрібно вказати табельний номер.")
    if not normalized_full_name:
        raise ValueError("Потрібно вказати ПІБ працівника.")
    if not normalized_department_name:
        raise ValueError("Потрібно вказати підрозділ.")
    if not normalized_position_name:
        raise ValueError("Потрібно вказати посаду.")
    normalized_source_photo_path = source_photo_path.strip() if source_photo_path else ""

    connection = create_database_connection(database_path)
    try:
        existing_row = connection.execute(
            """
            SELECT photo_path
            FROM employees
            WHERE personnel_number = ?;
            """,
            (normalized_personnel_number,),
        ).fetchone()

        if existing_row is None:
            raise ValueError("Працівника з таким табельним номером не знайдено.")

        existing_photo_path = existing_row[0]
        resolved_photo_relative_path = existing_photo_path

        if remove_photo:
            resolved_photo_relative_path = None
        elif normalized_source_photo_path:
            resolved_photo_relative_path = _copy_employee_photo_to_storage(
                database_path=database_path,
                personnel_number=normalized_personnel_number,
                source_photo_path=normalized_source_photo_path,
            )

        employee = Employee(
            personnel_number=normalized_personnel_number,
            full_name=normalized_full_name,
            position_name=normalized_position_name,
            department_name=normalized_department_name,
            employment_status=normalized_status,
            photo_path=resolved_photo_relative_path,
        )
        upsert_employee_row(connection, employee)
        insert_audit_log(
            connection,
            event_type="employee.updated",
            module_name="employees",
            event_level="info",
            actor_name="system",
            entity_name=f"employee:{normalized_personnel_number}",
            result_status="success",
            description_text=(
                f"full_name={normalized_full_name};"
                f"department={normalized_department_name};"
                f"position={normalized_position_name};"
                f"status={normalized_status};"
                f"photo={'set' if resolved_photo_relative_path else 'none'}"
            ),
        )
        connection.commit()
    finally:
        connection.close()


def _copy_employee_photo_to_storage(database_path: Path, personnel_number: str, source_photo_path: str) -> str:
    source_path = Path(source_photo_path)
    if not source_path.is_file():
        raise ValueError("Вибране фото не знайдено на диску.")

    photos_directory = database_path.parent / "photos"
    photos_directory.mkdir(parents=True, exist_ok=True)
    extension = source_path.suffix.lower() or ".png"
    safe_extension = extension if extension in {".png", ".jpg", ".jpeg", ".webp", ".bmp"} else ".png"
    target_file_name = f"{personnel_number}{safe_extension}"
    target_path = photos_directory / target_file_name
    shutil.copy2(source_path, target_path)
    return f"photos/{target_file_name}"
