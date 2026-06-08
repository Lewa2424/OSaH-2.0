from osah.domain.entities.notification_item import NotificationItem
from osah.domain.entities.notification_kind import NotificationKind
from osah.domain.entities.notification_level import NotificationLevel
from osah.domain.entities.port_shift_checklist_row import PortShiftChecklistRow
from osah.domain.entities.port_shift_decision import PortShiftDecision
from osah.domain.entities.port_shift_trigger_stat import PortShiftTriggerStat


_DEFAULT_REPEAT_THRESHOLD: int = 3


# ###### ПОСТРОЕНИЕ УВЕДОМЛЕНИЙ ПОРТ-Р / BUILD PORT-R NOTIFICATIONS ######
def build_port_r_notifications(
    checklists: tuple[PortShiftChecklistRow, ...],
    trigger_stats: tuple[PortShiftTriggerStat, ...],
    cutoff_date: str,
    repeat_threshold: int = _DEFAULT_REPEAT_THRESHOLD,
) -> tuple[NotificationItem, ...]:
    """Возвращает активные уведомления инженеру по модулю ПОРТ-Р (STOP и повторяющиеся триггеры).
    Returns active engineer notifications for the PORT-R module (STOP decisions and recurring triggers).

    cutoff_date — нижняя граница shift_date (ISO РРРР-ММ-ДД), записи раньше неё игнорируются.
    cutoff_date is the lower bound of shift_date (ISO YYYY-MM-DD); earlier records are ignored.
    """

    notifications: list[NotificationItem] = []

    stop_by_passport: dict[int, list[PortShiftChecklistRow]] = {}
    for row in checklists:
        if row.shift_date < cutoff_date:
            continue
        if row.decision == PortShiftDecision.STOP:
            stop_by_passport.setdefault(row.passport_id, []).append(row)

    for rows in stop_by_passport.values():
        latest = max(rows, key=lambda item: item.shift_date)
        count = len(rows)
        notifications.append(
            NotificationItem(
                notification_kind=NotificationKind.CONTROL,
                notification_level=NotificationLevel.CRITICAL,
                source_module="port_r.shift",
                title_text="СТОП-рішення на ділянці",
                message_text=(
                    f"{latest.passport_code} / {latest.site_name}: зафіксовано СТОП-рішень — {count}"
                    f" (останнє {latest.shift_date}). Потрібен перегляд калібрування."
                ),
            )
        )

    for stat in trigger_stats:
        if stat.hit_count < repeat_threshold:
            continue
        notifications.append(
            NotificationItem(
                notification_kind=NotificationKind.CONTROL,
                notification_level=NotificationLevel.WARNING,
                source_module="port_r.trigger",
                title_text="Повторюваний тригер ділянки",
                message_text=(
                    f"{stat.passport_code} / {stat.site_name}: тригер «{stat.trigger_text}»"
                    f" спрацював {stat.hit_count} раз(ів) (останній {stat.last_shift_date})."
                    " Розгляньте перегляд порогів."
                ),
            )
        )

    return tuple(notifications)
