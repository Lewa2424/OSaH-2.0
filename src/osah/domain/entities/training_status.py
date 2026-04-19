from enum import StrEnum


class TrainingStatus(StrEnum):
    """Статуси запису інструктажу.
    Статусы записи инструктажа.
    """

    CURRENT = "current"
    WARNING = "warning"
    OVERDUE = "overdue"
