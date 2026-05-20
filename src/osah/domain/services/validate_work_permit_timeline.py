from datetime import datetime, timedelta

from osah.domain.entities.work_permit_record import WorkPermitRecord
from osah.domain.entities.work_permit_status import WorkPermitStatus
from osah.domain.services.parse_storage_datetime_text import parse_storage_datetime_text


MAX_WORK_PERMIT_BASE_DURATION = timedelta(days=15)
MAX_WORK_PERMIT_EXTENSION_DURATION = timedelta(days=15)


def validate_work_permit_base_timeline(starts_at: datetime, ends_at: datetime) -> None:
    """Перевіряє базовий строк наряду-допуску до першого продовження.
    Validates the base work-permit timeline before the first extension.
    """

    if ends_at <= starts_at:
        raise ValueError("Час завершення має бути пізніше часу початку.")
    if ends_at - starts_at > MAX_WORK_PERMIT_BASE_DURATION:
        raise ValueError("Первинний строк наряду-допуску не може перевищувати 15 календарних днів.")


def validate_work_permit_extension(
    work_permit_record: WorkPermitRecord,
    extended_until: datetime,
    current_moment: datetime | None = None,
) -> None:
    """Перевіряє можливість одноразового продовження наряду-допуску.
    Validates a one-time work-permit extension.
    """

    if work_permit_record.closed_at:
        raise ValueError("Закритий наряд-допуск не можна продовжити.")
    if work_permit_record.canceled_at:
        raise ValueError("Скасований наряд-допуск не можна продовжити.")
    if work_permit_record.extension_count >= 1:
        raise ValueError("Наряд-допуск уже був продовжений. Повторне продовження заборонено.")
    if work_permit_record.status not in {WorkPermitStatus.ACTIVE, WorkPermitStatus.WARNING, WorkPermitStatus.EXPIRED}:
        raise ValueError("Продовжити можна лише діючий або прострочений наряд-допуск.")

    reference_moment = current_moment or datetime.now()
    try:
        current_ends_at = parse_storage_datetime_text(work_permit_record.ends_at)
    except ValueError as error:
        raise ValueError("У наряді вказано некоректну дату або час. Продовження недоступне.") from error
    if extended_until <= current_ends_at:
        raise ValueError("Нова дата завершення має бути пізніше поточного строку наряду-допуску.")
    if extended_until - current_ends_at > MAX_WORK_PERMIT_EXTENSION_DURATION:
        raise ValueError("Продовження наряду-допуску не може перевищувати 15 календарних днів.")
    if work_permit_record.status in {WorkPermitStatus.ACTIVE, WorkPermitStatus.WARNING} and current_ends_at <= reference_moment:
        raise ValueError("Поточний строк наряду вже сплив. Оновіть статус запису та повторіть дію.")
