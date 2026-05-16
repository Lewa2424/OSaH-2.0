from osah.domain.entities.training_registry_filter import TrainingRegistryFilter


# ###### ФОРМАТУВАННЯ МІТКИ ФІЛЬТРА ІНСТРУКТАЖІВ / FORMAT TRAINING FILTER LABEL ######
def format_training_registry_filter_label(registry_filter: TrainingRegistryFilter) -> str:
    """Повертає локалізовану мітку фільтра реєстру інструктажів.
    Returns a localized label for the trainings registry filter.
    """

    if registry_filter == TrainingRegistryFilter.ALL:
        return "Усі"
    if registry_filter == TrainingRegistryFilter.CURRENT:
        return "Актуальні"
    if registry_filter == TrainingRegistryFilter.INVALID:
        return "Конфлікт"
    if registry_filter == TrainingRegistryFilter.WARNING:
        return "Потребують уваги"
    if registry_filter == TrainingRegistryFilter.OVERDUE:
        return "Прострочені"
    return "Відсутні"
