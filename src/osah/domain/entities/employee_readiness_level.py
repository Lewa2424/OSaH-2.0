from enum import StrEnum


class EmployeeReadinessLevel(StrEnum):
    """Рівень готовності працівника до виконання робіт для пов'язаних розділів.
    Employee work-readiness level for linked safety modules.
    """

    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"
