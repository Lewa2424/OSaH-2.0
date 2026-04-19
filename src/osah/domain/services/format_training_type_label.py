from osah.domain.entities.training_type import TrainingType


# ###### ФОРМАТУВАННЯ НАЗВИ ТИПУ ІНСТРУКТАЖУ / ФОРМАТИРОВАНИЕ НАЗВАНИЯ ТИПА ИНСТРУКТАЖА ######
def format_training_type_label(training_type: TrainingType) -> str:
    """Повертає локалізовану назву типу інструктажу.
    Возвращает локализованное название типа инструктажа.
    """

    if training_type == TrainingType.INTRODUCTORY:
        return "Вступний"
    if training_type == TrainingType.PRIMARY:
        return "Первинний"
    if training_type == TrainingType.REPEATED:
        return "Повторний"
    if training_type == TrainingType.UNSCHEDULED:
        return "Позаплановий"
    return "Цільовий"
