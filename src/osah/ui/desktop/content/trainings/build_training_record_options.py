from osah.domain.entities.training_record import TrainingRecord
from osah.domain.services.format_training_type_label import format_training_type_label


# ###### ПОБУДОВА ОПЦІЙ ІСНУЮЧИХ ІНСТРУКТАЖІВ / ПОСТРОЕНИЕ ОПЦИЙ СУЩЕСТВУЮЩИХ ИНСТРУКТАЖЕЙ ######
def build_training_record_options(training_records: tuple[TrainingRecord, ...]) -> tuple[str, ...]:
    """Повертає підписи записів інструктажів для вибору у формі редагування.
    Возвращает подписи записей инструктажей для выбора в форме редактирования.
    """

    return tuple(
        f"{training_record.record_id} | {training_record.employee_full_name} | {format_training_type_label(training_record.training_type)} | {training_record.event_date}"
        for training_record in training_records
        if training_record.record_id is not None
    )
