from enum import StrEnum


class EmployeeStatusLevel(StrEnum):
    """Рівень агрегованого стану працівника для реєстру і картки.
    Aggregated employee status level for registry and detail card.
    """

    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"
    RESTRICTED = "restricted"
    ARCHIVED = "archived"
