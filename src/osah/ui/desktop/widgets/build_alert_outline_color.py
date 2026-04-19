from osah.domain.entities.notification_level import NotificationLevel


# ###### ВИБІР КОЛЬОРУ КОНТУРУ ТРИВОГИ / ВЫБОР ЦВЕТА КОНТУРА ТРЕВОГИ ######
def build_alert_outline_color(notification_level: NotificationLevel | None) -> str | None:
    """Повертає колір контуру для критичного або попереджувального стану.
    Возвращает цвет контура для критического или предупреждающего состояния.
    """

    if notification_level == NotificationLevel.CRITICAL:
        return "#a64039"
    if notification_level == NotificationLevel.WARNING:
        return "#c2813f"
    return None
