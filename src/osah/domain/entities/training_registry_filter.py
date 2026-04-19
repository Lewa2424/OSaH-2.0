from enum import StrEnum


class TrainingRegistryFilter(StrEnum):
    """Фільтри реєстру інструктажів.
    Фильтры реестра инструктажей.
    """

    ALL = "all"
    CURRENT = "current"
    WARNING = "warning"
    OVERDUE = "overdue"
    MISSING = "missing"
