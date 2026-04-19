from sqlite3 import Connection

from osah.domain.entities.notification_item import NotificationItem
from osah.domain.entities.notification_kind import NotificationKind
from osah.domain.entities.notification_level import NotificationLevel


# ###### ЧИТАННЯ АКТИВНИХ СПОВІЩЕНЬ / ЧТЕНИЕ АКТИВНЫХ УВЕДОМЛЕНИЙ ######
def list_notifications(connection: Connection) -> tuple[NotificationItem, ...]:
    """Повертає активні матеріалізовані сповіщення з локальної БД.
    Возвращает активные материализованные уведомления из локальной БД.
    """

    rows = connection.execute(
        """
        SELECT
            notification_kind,
            notification_level,
            source_module,
            title_text,
            message_text,
            employee_personnel_number,
            employee_full_name
        FROM notifications
        WHERE state_name = 'active'
        ORDER BY
            CASE notification_level
                WHEN 'critical' THEN 1
                WHEN 'warning' THEN 2
                ELSE 3
            END,
            id ASC;
        """
    ).fetchall()
    return tuple(
        NotificationItem(
            notification_kind=NotificationKind(row["notification_kind"]),
            notification_level=NotificationLevel(row["notification_level"]),
            source_module=row["source_module"],
            title_text=row["title_text"],
            message_text=row["message_text"],
            employee_personnel_number=row["employee_personnel_number"],
            employee_full_name=row["employee_full_name"],
        )
        for row in rows
    )
