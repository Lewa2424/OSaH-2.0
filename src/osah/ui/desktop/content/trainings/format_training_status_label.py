from osah.domain.entities.training_status import TrainingStatus


# ###### ФОРМАТУВАННЯ СТАТУСУ ІНСТРУКТАЖУ / ФОРМАТИРОВАНИЕ СТАТУСА ИНСТРУКТАЖА ######
def format_training_status_label(training_status: TrainingStatus) -> str:
    """Повертає локалізовану мітку статусу інструктажу.
    Возвращает локализованную метку статуса инструктажа.
    """

    if training_status == TrainingStatus.CURRENT:
        return "Актуально"
    if training_status == TrainingStatus.WARNING:
        return "Увага"
    return "Прострочено"
