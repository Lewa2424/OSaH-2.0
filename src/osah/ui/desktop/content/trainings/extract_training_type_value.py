from osah.domain.entities.training_type import TrainingType
from osah.domain.services.format_training_type_label import format_training_type_label


# ###### ВИДІЛЕННЯ ЗНАЧЕННЯ ТИПУ ІНСТРУКТАЖУ / ВЫДЕЛЕНИЕ ЗНАЧЕНИЯ ТИПА ИНСТРУКТАЖА ######
def extract_training_type_value(training_type_label: str) -> str:
    """Повертає технічне значення типу інструктажу за локалізованим підписом.
    Возвращает техническое значение типа инструктажа по локализованной подписи.
    """

    for training_type in TrainingType:
        if format_training_type_label(training_type) == training_type_label:
            return training_type.value
    return ""
