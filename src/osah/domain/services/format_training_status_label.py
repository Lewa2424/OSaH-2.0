from osah.domain.entities.training_registry_filter import TrainingRegistryFilter
from osah.domain.entities.training_status import TrainingStatus


# ###### ФОРМАТИРОВАНИЕ СТАТУСА ИНСТРУКТАЖА / FORMAT TRAINING STATUS ######
def format_training_status_label(status: TrainingStatus | TrainingRegistryFilter) -> str:
    """Возвращает украинскую подпись статуса инструктажа.
    Returns a Ukrainian label for a training status.
    """

    if status in {TrainingStatus.CURRENT, TrainingRegistryFilter.CURRENT}:
        return "Актуально"
    if status == TrainingStatus.NOT_REQUIRED:
        return "Не потрібно"
    if status == TrainingStatus.CLOSED_BY_PRIMARY:
        return "Закрито"
    if status in {TrainingStatus.WARNING, TrainingRegistryFilter.WARNING}:
        return "Увага"
    if status in {TrainingStatus.OVERDUE, TrainingRegistryFilter.OVERDUE}:
        return "Критично"
    if status in {TrainingStatus.MISSING, TrainingRegistryFilter.MISSING}:
        return "Відсутній"
    return "Архів"
