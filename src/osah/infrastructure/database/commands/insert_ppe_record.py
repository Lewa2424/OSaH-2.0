from sqlite3 import Connection

from osah.domain.entities.ppe_record import PpeRecord


# ###### ДОБАВЛЕНИЕ ЗАПИСИ СИЗ / INSERT PPE RECORD ######
def insert_ppe_record(connection: Connection, ppe_record: PpeRecord) -> None:
    """Сохраняет новую запись СИЗ вместе с полями нормативного контроля.
    Persists a new PPE record together with normative-control fields.
    """

    connection.execute(
        """
        INSERT INTO ppe_records (
            employee_personnel_number,
            ppe_name,
            is_required,
            is_issued,
            issue_date,
            replacement_date,
            quantity,
            note_text,
            provision_status,
            compliance_check_state,
            basis_text,
            basis_note
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
        (
            ppe_record.employee_personnel_number,
            ppe_record.ppe_name,
            1 if ppe_record.is_required else 0,
            1 if ppe_record.is_issued else 0,
            ppe_record.issue_date,
            ppe_record.replacement_date,
            ppe_record.quantity,
            ppe_record.note_text,
            ppe_record.provision_status.value,
            ppe_record.compliance_check_state.value,
            ppe_record.basis_text,
            ppe_record.basis_note,
        ),
    )
