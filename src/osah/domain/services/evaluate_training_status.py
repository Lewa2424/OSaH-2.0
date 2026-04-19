from datetime import date

from osah.domain.entities.training_record import TrainingRecord
from osah.domain.entities.training_status import TrainingStatus


# ###### ОЦІНКА СТАТУСУ ІНСТРУКТАЖУ / ОЦЕНКА СТАТУСА ИНСТРУКТАЖА ######
def evaluate_training_status(
    training_record: TrainingRecord,
    today: date | None = None,
    warning_days: int = 30,
) -> TrainingStatus:
    """Повертає статус запису інструктажу за датою наступного контролю.
    Возвращает статус записи инструктажа по дате следующего контроля.
    """

    current_date = today or date.today()
    next_control = date.fromisoformat(training_record.next_control_date)
    remaining_days = (next_control - current_date).days
    if remaining_days < 0:
        return TrainingStatus.OVERDUE
    if remaining_days <= warning_days:
        return TrainingStatus.WARNING
    return TrainingStatus.CURRENT
