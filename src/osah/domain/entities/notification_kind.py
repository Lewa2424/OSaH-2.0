from enum import StrEnum


class NotificationKind(StrEnum):
    """Типи сповіщень системи.
    Типы уведомлений системы.
    """

    CONTROL = "control"
    INFORMATION = "information"
