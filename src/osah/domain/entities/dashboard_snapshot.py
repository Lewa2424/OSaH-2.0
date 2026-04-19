from dataclasses import dataclass

from osah.domain.entities.news_item import NewsItem
from osah.domain.entities.notification_item import NotificationItem


@dataclass(slots=True)
class DashboardSnapshot:
    """Зведення стану для головного екрана.
    Сводка состояния для главного экрана.
    """

    employee_total: int
    critical_items: int
    warning_items: int
    focus_of_the_day: str
    active_notifications: tuple[NotificationItem, ...]
    unread_news_total: int
    latest_news_items: tuple[NewsItem, ...]
