from sqlite3 import Connection

from osah.domain.entities.training_record import TrainingRecord


# ###### ДОБАВЛЕНИЕ ЗАПИСИ ИНСТРУКТАЖА / INSERT TRAINING RECORD ######
def insert_training_record(connection: Connection, training_record: TrainingRecord) -> int:
    """Сохраняет новую запись инструктажа с нормативными полями.
    Persists a new training record including normative fields.
    """

    cursor = connection.execute(
        """
        INSERT INTO trainings (
            employee_personnel_number,
            training_type,
            event_date,
            next_control_date,
            conducted_by,
            note_text,
            person_category,
            requires_primary_on_workplace,
            work_risk_category,
            next_control_basis,
            knowledge_check_result,
            work_admission_status,
            knowledge_check_note,
            basis_text,
            basis_note,
            source_module,
            source_record_id,
            source_key
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
        (
            training_record.employee_personnel_number,
            training_record.training_type.value,
            training_record.event_date,
            training_record.next_control_date,
            training_record.conducted_by,
            training_record.note_text,
            training_record.person_category.value,
            int(training_record.requires_primary_on_workplace),
            training_record.work_risk_category.value,
            training_record.next_control_basis.value,
            training_record.knowledge_check_result.value,
            training_record.work_admission_status.value,
            training_record.knowledge_check_note,
            training_record.basis_text,
            training_record.basis_note,
            training_record.source_module,
            training_record.source_record_id,
            training_record.source_key,
        ),
    )
    return int(cursor.lastrowid)
