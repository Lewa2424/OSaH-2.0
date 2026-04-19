from osah.domain.entities.training_type import TrainingType
from osah.domain.services.format_training_type_label import format_training_type_label


# ###### ПОБУДОВА ОПЦІЙ ТИПІВ ІНСТРУКТАЖУ / ПОСТРОЕНИЕ ОПЦИЙ ТИПОВ ИНСТРУКТАЖА ######
def build_training_type_options() -> tuple[str, ...]:
    """Повертає локалізовані підписи типів інструктажу для форми.
    Возвращает локализованные подписи типов инструктажа для формы.
    """

    return tuple(format_training_type_label(training_type) for training_type in TrainingType)
