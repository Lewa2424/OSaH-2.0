from osah.domain.entities.notification_item import NotificationItem
from osah.domain.entities.notification_level import NotificationLevel


# ###### ПОБУДОВА ФОКУСУ ДНЯ / ПОСТРОЕНИЕ ФОКУСА ДНЯ ######
def build_focus_of_the_day(notifications: tuple[NotificationItem, ...]) -> str:
    """Будує короткий пріоритет дня за активними сповіщеннями.
    Строит короткий приоритет дня по активным уведомлениям.
    """

    if not notifications:
        return "Критичних або попереджувальних сигналів зараз немає. Можна переходити до доменних модулів контролю."

    critical_count = sum(
        1 for notification in notifications if notification.notification_level == NotificationLevel.CRITICAL
    )
    warning_count = sum(
        1 for notification in notifications if notification.notification_level == NotificationLevel.WARNING
    )
    if critical_count:
        return f"Насамперед потрібно прибрати {critical_count} критичних сигналів у картках працівників."
    return f"На старті варто закрити {warning_count} попереджень у реєстрі працівників."
