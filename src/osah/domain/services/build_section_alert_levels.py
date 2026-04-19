from osah.domain.entities.app_section import AppSection
from osah.domain.entities.notification_item import NotificationItem
from osah.domain.entities.notification_level import NotificationLevel
from osah.domain.services.get_higher_notification_level import get_higher_notification_level
from osah.domain.services.map_notification_to_app_section import map_notification_to_app_section


# ###### ПОБУДОВА РІВНІВ ТРИВОГИ РОЗДІЛІВ / ПОСТРОЕНИЕ УРОВНЕЙ ТРЕВОГИ РАЗДЕЛОВ ######
def build_section_alert_levels(
    notifications: tuple[NotificationItem, ...],
) -> dict[AppSection, NotificationLevel]:
    """Повертає найвищі рівні сигналізації для розділів shell.
    Возвращает наивысшие уровни сигнализации для разделов shell.
    """

    section_levels: dict[AppSection, NotificationLevel] = {}
    highest_level: NotificationLevel | None = None

    for notification in notifications:
        section = map_notification_to_app_section(notification)
        section_levels[section] = get_higher_notification_level(
            section_levels.get(section),
            notification.notification_level,
        )
        highest_level = get_higher_notification_level(highest_level, notification.notification_level)

    if highest_level is not None:
        section_levels[AppSection.DASHBOARD] = highest_level

    return section_levels
