from enum import StrEnum


class TrainingStatus(StrEnum):
    """Статуси запису інструктажу.
    Статусы записи инструктажа.
    """

    CURRENT = "current"
    WARNING = "warning"
    OVERDUE = "overdue"
    MISSING = "missing"
    NOT_REQUIRED = "not_required"
    CLOSED_BY_PRIMARY = "closed_by_primary"
