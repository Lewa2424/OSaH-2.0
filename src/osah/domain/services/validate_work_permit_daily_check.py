from datetime import datetime

from osah.domain.entities.work_permit_record import WorkPermitRecord


def validate_work_permit_daily_check(
    work_permit_record: WorkPermitRecord,
    checked_at: datetime,
    checked_by: str,
) -> None:
    """Перевіряє допустимість щоденної перевірки для наряду-допуску.
    Validates whether a daily check can be recorded for a work permit.
    """

    if work_permit_record.closed_at:
        raise ValueError("Закритий наряд не дозволяє фіксувати щоденні перевірки.")
    if work_permit_record.canceled_at:
        raise ValueError("Скасований наряд не дозволяє фіксувати щоденні перевірки.")
    if not checked_by.strip():
        raise ValueError("Потрібно вказати відповідального за щоденну перевірку.")

    starts_at = datetime.fromisoformat(work_permit_record.starts_at)
    ends_at = datetime.fromisoformat(work_permit_record.ends_at)
    if starts_at.date() == ends_at.date():
        raise ValueError("Щоденна перевірка потрібна лише для робіт тривалістю більше одного дня.")
    if checked_at.date() < starts_at.date() or checked_at.date() > ends_at.date():
        raise ValueError("Дата щоденної перевірки повинна потрапляти в строк дії наряду.")

    checked_date = checked_at.date().isoformat()
    if any(
        datetime.fromisoformat(daily_check.checked_at).date().isoformat() == checked_date
        for daily_check in work_permit_record.daily_checks
    ):
        raise ValueError("Щоденну перевірку за цю дату вже зафіксовано.")
