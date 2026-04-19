from osah.domain.entities.notification_level import NotificationLevel


# ###### ФОРМАТУВАННЯ РІВНЯ СПОВІЩЕННЯ / ФОРМАТИРОВАНИЕ УРОВНЯ УВЕДОМЛЕНИЯ ######
def format_notification_level_label(notification_level: NotificationLevel) -> str:
    """Повертає коротку локалізовану мітку рівня сповіщення.
    Возвращает короткую локализованную метку уровня уведомления.
    """

    if notification_level == NotificationLevel.CRITICAL:
        return "Критично"
    if notification_level == NotificationLevel.WARNING:
        return "Увага"
    return "Інфо"
