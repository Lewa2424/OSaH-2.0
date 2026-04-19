from osah.domain.entities.training_record import TrainingRecord
from osah.domain.services.format_training_type_label import format_training_type_label


# ###### СЕРІАЛІЗАЦІЯ ІНСТРУКТАЖУ ДЛЯ AUDIT / СЕРИАЛИЗАЦИЯ ИНСТРУКТАЖА ДЛЯ AUDIT ######
def serialize_training_record_for_audit(training_record: TrainingRecord) -> str:
    """Повертає компактний текстовий зліпок запису інструктажу для audit.
    Возвращает компактный текстовый слепок записи инструктажа для audit.
    """

    return (
        f"id={training_record.record_id}; "
        f"employee={training_record.employee_personnel_number}; "
        f"type={format_training_type_label(training_record.training_type)}; "
        f"event_date={training_record.event_date}; "
        f"next_control={training_record.next_control_date}; "
        f"conducted_by={training_record.conducted_by}; "
        f"note={training_record.note_text}"
    )
