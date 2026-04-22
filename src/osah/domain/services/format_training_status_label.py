from osah.domain.entities.training_registry_filter import TrainingRegistryFilter
from osah.domain.entities.training_status import TrainingStatus


# ###### ФОРМАТУВАННЯ СТАТУСУ ІНСТРУКТАЖУ / FORMAT TRAINING STATUS ######
def format_training_status_label(status: TrainingStatus | TrainingRegistryFilter) -> str:
    """Повертає україномовну назву статусу інструктажу.
    Returns a Ukrainian training status label.
    """

    if status in {TrainingStatus.CURRENT, TrainingRegistryFilter.CURRENT}:
        return "Актуально"
    if status in {TrainingStatus.WARNING, TrainingRegistryFilter.WARNING}:
        return "Увага"
    if status in {TrainingStatus.OVERDUE, TrainingRegistryFilter.OVERDUE}:
        return "Критично"
    if status == TrainingRegistryFilter.MISSING:
        return "Відсутній"
    return "Архів"
