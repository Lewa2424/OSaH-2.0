from osah.domain.entities.training_record import TrainingRecord
from osah.domain.services.format_training_type_label import format_training_type_label
from osah.ui.desktop.content.trainings.format_training_status_label import format_training_status_label


# ###### ПОБУДОВА ЗВЕДЕННЯ ІНСТРУКТАЖІВ ПРАЦІВНИКА / ПОСТРОЕНИЕ СВОДКИ ИНСТРУКТАЖЕЙ СОТРУДНИКА ######
def build_employee_training_summary(training_records: tuple[TrainingRecord, ...]) -> tuple[str, ...]:
    """Повертає короткі рядки для картки працівника по модулю інструктажів.
    Возвращает короткие строки для карточки сотрудника по модулю инструктажей.
    """

    if not training_records:
        return ("Записів інструктажів поки немає.",)

    sorted_records = sorted(training_records, key=lambda training_record: training_record.event_date, reverse=True)
    return tuple(
        f"{format_training_type_label(training_record.training_type)} | {training_record.event_date} | {format_training_status_label(training_record.status)}"
        for training_record in sorted_records[:3]
    )
