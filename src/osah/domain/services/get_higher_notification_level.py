from osah.domain.entities.notification_level import NotificationLevel


# ###### ВИБІР ВИЩОГО РІВНЯ СПОВІЩЕННЯ / ВЫБОР БОЛЕЕ ВЫСОКОГО УРОВНЯ УВЕДОМЛЕНИЯ ######
def get_higher_notification_level(
    current_level: NotificationLevel | None,
    candidate_level: NotificationLevel,
) -> NotificationLevel:
    """Повертає найвищий із двох рівнів пріоритету сповіщення.
    Возвращает наиболее высокий из двух уровней приоритета уведомления.
    """

    if current_level == NotificationLevel.CRITICAL or candidate_level == NotificationLevel.CRITICAL:
        return NotificationLevel.CRITICAL
    if current_level == NotificationLevel.WARNING or candidate_level == NotificationLevel.WARNING:
        return NotificationLevel.WARNING
    return NotificationLevel.INFO
