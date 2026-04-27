from pathlib import Path

from osah.infrastructure.database.commands.insert_audit_log import insert_audit_log
from osah.infrastructure.database.create_database_connection import create_database_connection


# ###### АРХІВУВАННЯ ПРАЦІВНИКА / ARCHIVE EMPLOYEE ######
def archive_employee(
    database_path: Path,
    personnel_number: str,
) -> None:
    """Переводить працівника в архівний статус та додає audit-лог.
    Sets employee status to archived and adds audit log.
    """

    normalized_personnel_number = personnel_number.strip()
    if not normalized_personnel_number:
        raise ValueError("Потрібно вказати табельний номер.")

    connection = create_database_connection(database_path)
    try:
        existing_row = connection.execute(
            """
            SELECT employment_status
            FROM employees
            WHERE personnel_number = ?;
            """,
            (normalized_personnel_number,),
        ).fetchone()

        if existing_row is None:
            raise ValueError("Працівника з таким табельним номером не знайдено.")

        connection.execute(
            """
            UPDATE employees
            SET employment_status = 'archived'
            WHERE personnel_number = ?;
            """,
            (normalized_personnel_number,),
        )

        insert_audit_log(
            connection,
            event_type="employee.archived",
            module_name="employees",
            event_level="warning",
            actor_name="system",
            entity_name=f"employee:{normalized_personnel_number}",
            result_status="success",
            description_text="Status changed to archived via UI",
        )
        connection.commit()
    finally:
        connection.close()
