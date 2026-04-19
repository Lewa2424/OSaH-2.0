from sqlite3 import Connection

from osah.domain.entities.notification_item import NotificationItem


# ###### ЗАМІНА АКТИВНИХ СПОВІЩЕНЬ / ЗАМЕНА АКТИВНЫХ УВЕДОМЛЕНИЙ ######
def replace_notifications(connection: Connection, notifications: tuple[NotificationItem, ...]) -> None:
    """Повністю оновлює матеріалізований набір активних сповіщень.
    Полностью обновляет материализованный набор активных уведомлений.
    """

    connection.execute("DELETE FROM notifications;")
    connection.executemany(
        """
        INSERT INTO notifications (
            notification_kind,
            notification_level,
            source_module,
            title_text,
            message_text,
            employee_personnel_number,
            employee_full_name,
            state_name
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """,
        [
            (
                notification.notification_kind.value,
                notification.notification_level.value,
                notification.source_module,
                notification.title_text,
                notification.message_text,
                notification.employee_personnel_number,
                notification.employee_full_name,
                "active",
            )
            for notification in notifications
        ],
    )
    connection.commit()
