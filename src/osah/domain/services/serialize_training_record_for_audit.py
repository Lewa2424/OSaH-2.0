from osah.domain.entities.training_record import TrainingRecord
from osah.domain.services.format_training_type_label import format_training_type_label


# ###### СЕРИАЛИЗАЦИЯ ИНСТРУКТАЖА ДЛЯ AUDIT / SERIALIZE TRAINING FOR AUDIT ######
def serialize_training_record_for_audit(training_record: TrainingRecord) -> str:
    """Возвращает компактный текстовый слепок записи инструктажа для audit.
    Returns a compact textual snapshot of a training record for audit.
    """

    return (
        f"id={training_record.record_id}; "
        f"employee={training_record.employee_personnel_number}; "
        f"type={format_training_type_label(training_record.training_type)}; "
        f"event_date={training_record.event_date}; "
        f"next_control={training_record.next_control_date}; "
        f"person_category={training_record.person_category.value}; "
        f"requires_primary={int(training_record.requires_primary_on_workplace)}; "
        f"risk={training_record.work_risk_category.value}; "
        f"basis={training_record.next_control_basis.value}; "
        f"knowledge_result={training_record.knowledge_check_result.value}; "
        f"admission={training_record.work_admission_status.value}; "
        f"knowledge_note={training_record.knowledge_check_note}; "
        f"basis_text={training_record.basis_text}; "
        f"basis_note={training_record.basis_note}; "
        f"conducted_by={training_record.conducted_by}; "
        f"note={training_record.note_text}"
    )
