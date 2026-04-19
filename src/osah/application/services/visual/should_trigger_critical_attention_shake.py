from datetime import datetime, timedelta

from osah.domain.entities.notification_level import NotificationLevel


# ###### ПЕРЕВІРКА ПОТРЕБИ У CRITICAL-SHAKE / ПРОВЕРКА НУЖНОСТИ CRITICAL-SHAKE ######
def should_trigger_critical_attention_shake(
    section_levels: dict[object, NotificationLevel],
    last_shake_at_text: str,
    current_moment: datetime | None = None,
) -> bool:
    """Повертає true, якщо критичне тремтіння можна виконати зараз.
    Возвращает true, если критическое дрожание можно выполнить сейчас.
    """

    if NotificationLevel.CRITICAL not in section_levels.values():
        return False

    if not last_shake_at_text.strip():
        return True

    reference_moment = current_moment or datetime.now()
    try:
        last_shake_at = datetime.fromisoformat(last_shake_at_text.strip())
    except ValueError:
        return True

    return reference_moment - last_shake_at >= timedelta(hours=2)
