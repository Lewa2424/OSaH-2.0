from datetime import datetime

from osah.domain.entities.work_permit_record import WorkPermitRecord
from osah.domain.entities.work_permit_status import WorkPermitStatus
from osah.domain.services.format_ui_datetime import format_ui_datetime
from osah.domain.services.parse_storage_datetime_text import parse_storage_datetime_text


def build_work_permit_daily_check_summary(work_permit_record: WorkPermitRecord | None) -> dict[str, object]:
    """Повертає тексти та прапорці для блоку щоденних перевірок у Qt.
    Returns texts and flags for the daily-check block in Qt.
    """

    if work_permit_record is None:
        return {
            "requirement_text": "Щоденні перевірки стануть доступні після збереження наряду.",
            "last_check_text": "Остання перевірка: -",
            "history_text": "Журнал перевірок: ще порожній",
            "can_record": False,
        }

    try:
        starts_at = parse_storage_datetime_text(work_permit_record.starts_at)
        ends_at = parse_storage_datetime_text(work_permit_record.ends_at)
    except ValueError:
        return {
            "requirement_text": "Неможливо оцінити щоденні перевірки: у наряді вказано некоректну дату або час.",
            "last_check_text": "Остання перевірка: -",
            "history_text": "Журнал перевірок: потрібна перевірка даних наряду",
            "can_record": False,
        }
    is_multiday = starts_at.date() != ends_at.date()
    latest_check = work_permit_record.daily_checks[-1] if work_permit_record.daily_checks else None
    history_text = (
        "Журнал перевірок: "
        + ", ".join(format_ui_datetime(check.checked_at) for check in work_permit_record.daily_checks)
        if work_permit_record.daily_checks
        else "Журнал перевірок: ще порожній"
    )

    if not is_multiday:
        requirement_text = "Для одноденного наряду окремі щоденні перевірки не вимагаються."
        can_record = False
    elif work_permit_record.status in {
        WorkPermitStatus.CLOSED,
        WorkPermitStatus.CANCELED,
        WorkPermitStatus.REISSUED,
    }:
        requirement_text = "Для закритого, скасованого або перевипущеного наряду нові щоденні перевірки недоступні."
        can_record = False
    else:
        requirement_text = "Для багатоденного наряду місце робіт потрібно перевіряти щодня з окремою відміткою."
        can_record = True

    return {
        "requirement_text": requirement_text,
        "last_check_text": (
            f"Остання перевірка: {format_ui_datetime(latest_check.checked_at)} — {latest_check.checked_by}"
            if latest_check
            else "Остання перевірка: -"
        ),
        "history_text": history_text,
        "can_record": can_record,
    }
