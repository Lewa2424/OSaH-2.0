from enum import StrEnum


class PpeStatus(StrEnum):
    """Статуси запису ЗІЗ.
    Статусы записи СИЗ.
    """

    CURRENT = "current"
    WARNING = "warning"
    EXPIRED = "expired"
    NOT_ISSUED = "not_issued"
