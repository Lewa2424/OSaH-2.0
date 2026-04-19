from enum import StrEnum


class NotificationLevel(StrEnum):
    """Рівні сповіщень системи.
    Уровни уведомлений системы.
    """

    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"
