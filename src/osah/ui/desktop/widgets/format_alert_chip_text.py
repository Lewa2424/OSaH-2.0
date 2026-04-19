from osah.domain.entities.notification_level import NotificationLevel


# ###### ФОРМАТУВАННЯ ТЕКСТУ ALERT-CHIP / ФОРМАТИРОВАНИЕ ТЕКСТА ALERT-CHIP ######
def format_alert_chip_text(notification_level: NotificationLevel | None) -> str:
    """Повертає короткий текстовий стан для візуального alert-chip.
    Возвращает короткое текстовое состояние для визуального alert-chip.
    """

    if notification_level == NotificationLevel.CRITICAL:
        return "Критично"
    if notification_level == NotificationLevel.WARNING:
        return "Увага"
    return "Стабільно"
