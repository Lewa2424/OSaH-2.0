from enum import StrEnum


class TrainingPersonCategory(StrEnum):
    """Категории лиц в контексте инструктажа.
    Person categories used in the training context.
    """

    OWN_EMPLOYEE = "own_employee"
    CONTRACTOR = "contractor"
    SECONDED_WORKER = "seconded_worker"
    VISITOR = "visitor"
    STUDENT_INTERN = "student_intern"
