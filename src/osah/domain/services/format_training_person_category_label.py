from osah.domain.entities.training_person_category import TrainingPersonCategory


# ###### ПОДПИСЬ КАТЕГОРИИ ЛИЦА ДЛЯ ИНСТРУКТАЖА / FORMAT TRAINING PERSON CATEGORY LABEL ######
def format_training_person_category_label(person_category: TrainingPersonCategory) -> str:
    """Возвращает понятную подпись категории лица для формы и списка.
    Returns a readable person category label for forms and lists.
    """

    labels = {
        TrainingPersonCategory.OWN_EMPLOYEE: "Власний працівник підприємства",
        TrainingPersonCategory.CONTRACTOR: "Підрядник / стороння організація",
        TrainingPersonCategory.SECONDED_WORKER: "Відряджений працівник",
        TrainingPersonCategory.VISITOR: "Відвідувач / екскурсант",
        TrainingPersonCategory.STUDENT_INTERN: "Студент / практикант",
    }
    return labels[person_category]
