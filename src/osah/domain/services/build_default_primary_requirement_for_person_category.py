from osah.domain.entities.training_person_category import TrainingPersonCategory


# ###### ТИПОВОЕ ТРЕБОВАНИЕ ПЕРВИЧНОГО ПО КАТЕГОРИИ ЛИЦА / BUILD DEFAULT PRIMARY REQUIREMENT ######
def build_default_primary_requirement_for_person_category(
    person_category: TrainingPersonCategory,
) -> bool:
    """Возвращает рекомендуемое значение требования первичного для категории лица.
    Returns the recommended default primary-training requirement for a person category.
    """

    return person_category == TrainingPersonCategory.OWN_EMPLOYEE
