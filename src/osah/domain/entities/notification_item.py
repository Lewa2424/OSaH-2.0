from dataclasses import dataclass

from osah.domain.entities.notification_kind import NotificationKind
from osah.domain.entities.notification_level import NotificationLevel


@dataclass(slots=True)
class NotificationItem:
    """Активне системне сповіщення.
    Активное системное уведомление.
    """

    notification_kind: NotificationKind
    notification_level: NotificationLevel
    source_module: str
    title_text: str
    message_text: str
    employee_personnel_number: str | None = None
    employee_full_name: str | None = None
