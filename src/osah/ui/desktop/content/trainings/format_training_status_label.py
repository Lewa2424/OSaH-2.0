from osah.domain.entities.training_status import TrainingStatus


# ###### ФОРМАТИРОВАНИЕ СТАТУСА ИНСТРУКТАЖА / FORMAT TRAINING STATUS LABEL ######
def format_training_status_label(training_status: TrainingStatus) -> str:
    """Возвращает локализованную метку статуса инструктажа.
    Returns a localized label for a training status.
    """

    if training_status == TrainingStatus.CURRENT:
        return "Актуально"
    if training_status == TrainingStatus.NOT_REQUIRED:
        return "Не потрібно"
    if training_status == TrainingStatus.CLOSED_BY_PRIMARY:
        return "Закрито"
    if training_status == TrainingStatus.WARNING:
        return "Увага"
    if training_status == TrainingStatus.MISSING:
        return "Відсутній"
    return "Прострочено"
