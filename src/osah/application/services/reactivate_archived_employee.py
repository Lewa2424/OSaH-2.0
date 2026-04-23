from pathlib import Path

from osah.domain.entities.employee import Employee
from osah.infrastructure.database.commands.insert_audit_log import insert_audit_log
from osah.infrastructure.database.commands.upsert_employee_row import upsert_employee_row
from osah.infrastructure.database.create_database_connection import create_database_connection


# ###### РЕАКТИВАЦІЯ АРХІВНОГО ПРАЦІВНИКА / REACTIVATE ARCHIVED EMPLOYEE ######
def reactivate_archived_employee(database_path: Path, personnel_number: str) -> None:
    """Reactivates archived employee by setting employment status to active."""

    connection = create_database_connection(database_path)
    try:
        row = connection.execute(
            """
            SELECT personnel_number, full_name, position_name, department_name, employment_status
            FROM employees
            WHERE personnel_number = ?;
            """,
            (personnel_number,),
        ).fetchone()
        if row is None:
            raise ValueError("Працівника не знайдено.")

        current_status = str(row["employment_status"]).lower()
        if current_status not in {"archived", "inactive", "dismissed"}:
            raise ValueError("Працівник вже активний.")

        upsert_employee_row(
            connection,
            Employee(
                personnel_number=str(row["personnel_number"]),
                full_name=str(row["full_name"]),
                position_name=str(row["position_name"]),
                department_name=str(row["department_name"]),
                employment_status="active",
            ),
        )
        insert_audit_log(
            connection,
            event_type="employee.reactivated",
            module_name="archive",
            event_level="warning",
            actor_name="inspector",
            entity_name=str(row["personnel_number"]),
            result_status="success",
            description_text="Archived employee reactivated from archive registry.",
        )
        connection.commit()
    finally:
        connection.close()
