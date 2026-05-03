from osah.domain.entities.training_person_category import TrainingPersonCategory


# ###### ОБЯЗАН ЛИ КОНТЕКСТ ТРЕБОВАТЬ ПЕРВИЧНЫЙ ИНСТРУКТАЖ / DOES TRAINING CONTEXT REQUIRE PRIMARY ######
def does_training_context_require_primary(
    person_category: TrainingPersonCategory,
    requires_primary_on_workplace: bool,
) -> bool:
    """Определяет, требует ли контекст записи первичный инструктаж на рабочем месте.
    Determines whether the record context requires primary training at the workplace.
    """

    if person_category == TrainingPersonCategory.VISITOR:
        return False
    return requires_primary_on_workplace
