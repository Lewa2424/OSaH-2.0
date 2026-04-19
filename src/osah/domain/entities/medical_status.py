from enum import StrEnum


class MedicalStatus(StrEnum):
    """Статуси медичного запису.
    Статусы медицинской записи.
    """

    CURRENT = "current"
    WARNING = "warning"
    EXPIRED = "expired"
    RESTRICTED = "restricted"
    NOT_FIT = "not_fit"
