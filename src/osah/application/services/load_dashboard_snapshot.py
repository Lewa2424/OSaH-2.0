from sqlite3 import Connection

from osah.domain.entities.dashboard_snapshot import DashboardSnapshot
from osah.domain.entities.notification_level import NotificationLevel
from osah.domain.services.build_focus_of_the_day import build_focus_of_the_day
from osah.infrastructure.database.queries.count_employees import count_employees
from osah.infrastructure.database.queries.count_unread_news_items import count_unread_news_items
from osah.infrastructure.database.queries.list_news_items import list_news_items
from osah.infrastructure.database.queries.list_notifications import list_notifications


# ###### ЗНІМОК ГОЛОВНОГО ЕКРАНА / СНИМОК ГЛАВНОГО ЭКРАНА ######
def load_dashboard_snapshot(connection: Connection) -> DashboardSnapshot:
    """Збирає базове управлінське зведення для головного екрана.
    Собирает базовую управленческую сводку для главного экрана.
    """

    employee_total = count_employees(connection)
    notifications = list_notifications(connection)
    latest_news_items = list_news_items(connection, unread_only=True)[:5]
    return DashboardSnapshot(
        employee_total=employee_total,
        critical_items=sum(
            1 for notification in notifications if notification.notification_level == NotificationLevel.CRITICAL
        ),
        warning_items=sum(
            1 for notification in notifications if notification.notification_level == NotificationLevel.WARNING
        ),
        focus_of_the_day=build_focus_of_the_day(notifications),
        active_notifications=notifications,
        unread_news_total=count_unread_news_items(connection),
        latest_news_items=latest_news_items,
    )
