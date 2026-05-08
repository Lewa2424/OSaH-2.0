from sqlite3 import Connection

from osah.domain.entities.training_record import TrainingRecord


# ###### ОБНОВЛЕНИЕ ЗАПИСИ ИНСТРУКТАЖА / UPDATE TRAINING RECORD ######
def update_training_record_row(connection: Connection, training_record: TrainingRecord) -> None:
    """Обновляет существующую запись инструктажа со всеми новыми полями.
    Updates an existing training record with all new fields.
    """

    connection.execute(
        """
        UPDATE trainings
        SET
            employee_personnel_number = ?,
            training_type = ?,
            event_date = ?,
            next_control_date = ?,
            conducted_by = ?,
            note_text = ?,
            person_category = ?,
            requires_primary_on_workplace = ?,
            work_risk_category = ?,
            next_control_basis = ?,
            knowledge_check_result = ?,
            work_admission_status = ?,
            knowledge_check_note = ?,
            basis_text = ?,
            basis_note = ?,
            is_current = ?,
            archived_at = ?,
            archive_reason = ?,
            replaced_by_record_id = ?,
            source_module = ?,
            source_record_id = ?,
            source_key = ?
        WHERE id = ?;
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
            int(training_record.is_current),
            training_record.archived_at,
            training_record.archive_reason,
            training_record.replaced_by_record_id,
            training_record.source_module,
            training_record.source_record_id,
            training_record.source_key,
            training_record.record_id,
        ),
    )
