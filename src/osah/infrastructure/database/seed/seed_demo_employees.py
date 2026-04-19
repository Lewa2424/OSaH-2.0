from sqlite3 import Connection

from osah.infrastructure.database.seed.build_demo_employee_rows import build_demo_employee_rows
from osah.infrastructure.database.seed.build_demo_medical_rows import build_demo_medical_rows
from osah.infrastructure.database.seed.build_demo_ppe_rows import build_demo_ppe_rows
from osah.infrastructure.database.seed.build_demo_training_rows import build_demo_training_rows
from osah.infrastructure.database.seed.build_demo_work_permit_rows import build_demo_work_permit_rows


# ###### ЗАПОВНЕННЯ ДЕМОДАНИМИ ПІДПРИЄМСТВА / ЗАПОЛНЕНИЕ ДЕМОДАННЫМИ ПРЕДПРИЯТИЯ ######
def seed_demo_employees(connection: Connection) -> None:
    """Створює типове наповнення бази даних для першого запуску локальної системи.
    Создает типовое наполнение базы данных для первого запуска локальной системы.
    """

    employee_exists = connection.execute("SELECT 1 FROM employees LIMIT 1;").fetchone()
    if employee_exists:
        return

    employee_rows = build_demo_employee_rows()
    training_rows = build_demo_training_rows(employee_rows)
    ppe_rows = build_demo_ppe_rows(employee_rows)
    medical_rows = build_demo_medical_rows(employee_rows)
    work_permit_rows, work_permit_participants = build_demo_work_permit_rows(employee_rows)

    connection.executemany(
        """
        INSERT INTO employees (
            personnel_number,
            full_name,
            position_name,
            department_name,
            employment_status
        )
        VALUES (?, ?, ?, ?, ?);
        """,
        employee_rows,
    )
    connection.executemany(
        """
        INSERT INTO trainings (
            employee_personnel_number,
            training_type,
            event_date,
            next_control_date,
            conducted_by,
            note_text
        )
        VALUES (?, ?, ?, ?, ?, ?);
        """,
        training_rows,
    )
    connection.executemany(
        """
        INSERT INTO ppe_records (
            employee_personnel_number,
            ppe_name,
            is_required,
            is_issued,
            issue_date,
            replacement_date,
            quantity,
            note_text
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """,
        ppe_rows,
    )
    connection.executemany(
        """
        INSERT INTO medical_records (
            employee_personnel_number,
            valid_from,
            valid_until,
            medical_decision,
            restriction_note
        )
        VALUES (?, ?, ?, ?, ?);
        """,
        medical_rows,
    )
    connection.executemany(
        """
        INSERT INTO work_permits (
            permit_number,
            work_kind,
            work_location,
            starts_at,
            ends_at,
            responsible_person,
            issuer_person,
            note_text,
            closed_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
        work_permit_rows,
    )

    work_permit_id_by_number = {
        row["permit_number"]: int(row["id"])
        for row in connection.execute("SELECT id, permit_number FROM work_permits;").fetchall()
    }
    connection.executemany(
        """
        INSERT INTO work_permit_participants (
            work_permit_id,
            employee_personnel_number,
            participant_role
        )
        VALUES (?, ?, ?);
        """,
        [
            (work_permit_id_by_number[permit_number], employee_personnel_number, participant_role)
            for permit_number, employee_personnel_number, participant_role in work_permit_participants
        ],
    )
    connection.execute(
        """
        INSERT INTO audit_log (
            event_type,
            module_name,
            event_level,
            actor_name,
            entity_name,
            result_status,
            description_text
        )
        VALUES (?, ?, ?, ?, ?, ?, ?);
        """,
        (
            "application.bootstrap",
            "database.seed",
            "info",
            "system",
            "demo.enterprise",
            "success",
            "Demo enterprise dataset created with employees, trainings, PPE, medical records and work permits.",
        ),
    )
    connection.commit()
