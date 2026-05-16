from pathlib import Path

from osah.application.services.sync_control_notifications import sync_control_notifications
from osah.domain.entities.training_knowledge_check_result import TrainingKnowledgeCheckResult
from osah.domain.entities.training_person_category import TrainingPersonCategory
from osah.domain.entities.training_record import TrainingRecord
from osah.domain.entities.training_status import TrainingStatus
from osah.domain.entities.training_type import TrainingType
from osah.domain.entities.training_work_admission_status import TrainingWorkAdmissionStatus
from osah.domain.entities.training_work_risk_category import TrainingWorkRiskCategory
from osah.domain.services.find_training_chronology_conflict_reason import find_training_chronology_conflict_reason
from osah.domain.services.parse_ui_date_text import parse_ui_date_text
from osah.domain.services.resolve_training_next_control_date import resolve_training_next_control_date
from osah.domain.services.serialize_training_record_for_audit import serialize_training_record_for_audit
from osah.infrastructure.database.commands.archive_training_record_row import archive_training_record_row
from osah.infrastructure.database.commands.insert_audit_log import insert_audit_log
from osah.infrastructure.database.commands.insert_training_record import insert_training_record
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.get_training_record_by_id import get_training_record_by_id
from osah.infrastructure.database.queries.list_training_records import list_training_records


def create_current_training_record(
    database_path: Path,
    employee_personnel_number: str,
    training_type: str,
    event_date_text: str,
    next_control_date_text: str,
    conducted_by: str,
    note_text: str,
    person_category: str = "own_employee",
    requires_primary_on_workplace: bool = True,
    work_risk_category: str = "not_applicable",
    should_update_repeated_control: bool = False,
    use_manual_next_control_date: bool = False,
    knowledge_check_result: str = "legacy_not_tracked",
    work_admission_status: str = "legacy_not_tracked",
    knowledge_check_note: str = "",
    basis_text: str = "",
    basis_note: str = "",
    source_module: str = "",
    source_record_id: int | None = None,
    source_key: str = "",
) -> int:
    """Створює новий актуальний інструктаж і архівує попередній current того ж слота.
    Creates a new current training record and archives the previous current record in the same slot.
    """

    normalized_personnel_number = employee_personnel_number.strip()
    normalized_conducted_by = conducted_by.strip()
    normalized_note = note_text.strip()
    normalized_training_type = training_type.strip()
    normalized_person_category = person_category.strip() or "own_employee"
    normalized_work_risk_category = work_risk_category.strip() or "not_applicable"
    normalized_knowledge_check_note = knowledge_check_note.strip()
    normalized_basis_text = basis_text.strip()
    normalized_basis_note = basis_note.strip()
    normalized_source_module = source_module.strip()
    normalized_source_key = source_key.strip()
    if not normalized_personnel_number:
        raise ValueError("Потрібно вибрати працівника.")
    if not normalized_training_type:
        raise ValueError("Потрібно вибрати тип інструктажу.")
    if not normalized_conducted_by:
        raise ValueError("Потрібно вказати, хто проводив інструктаж.")

    event_date = parse_ui_date_text(event_date_text)
    manual_next_control_date = parse_ui_date_text(next_control_date_text) if next_control_date_text.strip() else None
    training_type_value = TrainingType(normalized_training_type)
    resolved_next_control_date, next_control_basis, resolved_work_risk_category = resolve_training_next_control_date(
        training_type_value,
        event_date,
        TrainingPersonCategory(normalized_person_category),
        requires_primary_on_workplace,
        TrainingWorkRiskCategory(normalized_work_risk_category),
        manual_next_control_date,
        should_update_repeated_control,
        use_manual_next_control_date,
    )
    if manual_next_control_date is not None and manual_next_control_date < event_date:
        raise ValueError("Дата наступного контролю не може бути раніше дати проведення.")

    connection = create_database_connection(database_path)
    try:
        previous_record_ids = _find_current_record_ids_for_replacement(
            connection,
            normalized_personnel_number,
            training_type_value,
            normalized_source_module,
            normalized_source_key,
        )
        training_record = TrainingRecord(
            record_id=None,
            employee_personnel_number=normalized_personnel_number,
            employee_full_name="",
            training_type=training_type_value,
            event_date=event_date.isoformat(),
            next_control_date=resolved_next_control_date,
            conducted_by=normalized_conducted_by,
            note_text=normalized_note,
            status=TrainingStatus.CURRENT,
            person_category=TrainingPersonCategory(normalized_person_category),
            requires_primary_on_workplace=requires_primary_on_workplace,
            work_risk_category=resolved_work_risk_category,
            next_control_basis=next_control_basis,
            knowledge_check_result=TrainingKnowledgeCheckResult(knowledge_check_result.strip() or "legacy_not_tracked"),
            work_admission_status=TrainingWorkAdmissionStatus(work_admission_status.strip() or "legacy_not_tracked"),
            knowledge_check_note=normalized_knowledge_check_note,
            basis_text=normalized_basis_text,
            basis_note=normalized_basis_note,
            is_current=True,
            archived_at=None,
            archive_reason="",
            replaced_by_record_id=None,
            source_module=normalized_source_module,
            source_record_id=source_record_id,
            source_key=normalized_source_key,
        )
        chronology_conflict_reason = find_training_chronology_conflict_reason(
            training_record,
            tuple(
                record
                for record in list_training_records(connection)
                if record.employee_personnel_number == normalized_personnel_number
            ),
        )
        if chronology_conflict_reason is not None:
            raise ValueError(chronology_conflict_reason)
        created_record_id = insert_training_record(connection, training_record)
        created_record = get_training_record_by_id(connection, created_record_id)

        for previous_record_id in previous_record_ids:
            previous_record = get_training_record_by_id(connection, previous_record_id)
            archive_training_record_row(
                connection,
                previous_record_id,
                archive_reason=_build_archive_reason(training_type_value, normalized_source_module),
                replaced_by_record_id=created_record_id,
            )
            if previous_record is not None:
                insert_audit_log(
                    connection,
                    event_type="training.replaced",
                    module_name="trainings",
                    event_level="info",
                    actor_name="system",
                    entity_name=f"training:{normalized_personnel_number}:{training_type_value.value}",
                    result_status="success",
                    description_text=(
                        f"employee_personnel_number={normalized_personnel_number}; "
                        f"training_type={training_type_value.value}; "
                        f"old_record_id={previous_record_id}; "
                        f"new_record_id={created_record_id}; "
                        f"archive_reason={_build_archive_reason(training_type_value, normalized_source_module)}; "
                        f"old=({serialize_training_record_for_audit(previous_record)})"
                    ),
                )

        insert_audit_log(
            connection,
            event_type="training.created",
            module_name="trainings",
            event_level="info",
            actor_name="system",
            entity_name=f"training:{normalized_personnel_number}",
            result_status="success",
            description_text=f"created=({serialize_training_record_for_audit(created_record or training_record)})",
        )
        sync_control_notifications(connection)
        connection.commit()
        return created_record_id
    finally:
        connection.close()


def _find_current_record_ids_for_replacement(
    connection,
    employee_personnel_number: str,
    training_type: TrainingType,
    source_module: str,
    source_key: str,
) -> tuple[int, ...]:
    if training_type == TrainingType.TARGETED:
        if source_module == "work_permits" and source_key:
            rows = connection.execute(
                """
                SELECT id
                FROM trainings
                WHERE source_module = ? AND source_key = ? AND is_current = 1
                ORDER BY event_date DESC, id DESC;
                """,
                (source_module, source_key),
            ).fetchall()
            return tuple(int(row["id"]) for row in rows)
        rows = connection.execute(
            """
            SELECT id
            FROM trainings
            WHERE employee_personnel_number = ?
              AND training_type = 'targeted'
              AND is_current = 1
              AND source_module = ''
            ORDER BY event_date DESC, id DESC;
            """,
            (employee_personnel_number,),
        ).fetchall()
        return tuple(int(row["id"]) for row in rows)

    rows = connection.execute(
        """
        SELECT id
        FROM trainings
        WHERE employee_personnel_number = ?
          AND training_type = ?
          AND is_current = 1
        ORDER BY event_date DESC, id DESC;
        """,
        (employee_personnel_number, training_type.value),
    ).fetchall()
    return tuple(int(row["id"]) for row in rows)


def _build_archive_reason(training_type: TrainingType, source_module: str) -> str:
    if training_type == TrainingType.TARGETED and source_module == "work_permits":
        return "replaced_by_work_permit_target_training"
    return "replaced_by_new_training"
