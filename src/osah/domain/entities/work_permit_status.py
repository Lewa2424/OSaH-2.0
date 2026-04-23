from enum import StrEnum


class WorkPermitStatus(StrEnum):
    """Статуси наряду-допуску.
    Статусы наряда-допуска.
    """

    ACTIVE = "active"
    WARNING = "warning"
    EXPIRED = "expired"
    CLOSED = "closed"
    CANCELED = "canceled"
    INVALID = "invalid"
