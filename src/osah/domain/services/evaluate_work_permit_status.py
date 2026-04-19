from datetime import datetime

from osah.domain.entities.work_permit_record import WorkPermitRecord
from osah.domain.entities.work_permit_status import WorkPermitStatus


# ###### ОЦІНКА СТАТУСУ НАРЯДУ-ДОПУСКУ / ОЦЕНКА СТАТУСА НАРЯДА-ДОПУСКА ######
def evaluate_work_permit_status(
    work_permit_record: WorkPermitRecord,
    current_moment: datetime | None = None,
    warning_days: int = 3,
) -> WorkPermitStatus:
    """Повертає статус наряду-допуску за строком завершення та фактом ручного закриття.
    Возвращает статус наряда-допуска по сроку завершения и факту ручного закрытия.
    """

    if work_permit_record.closed_at:
        return WorkPermitStatus.CLOSED

    reference_moment = current_moment or datetime.now()
    ends_at = datetime.fromisoformat(work_permit_record.ends_at)
    remaining_seconds = (ends_at - reference_moment).total_seconds()
    if remaining_seconds < 0:
        return WorkPermitStatus.EXPIRED
    if remaining_seconds <= warning_days * 24 * 60 * 60:
        return WorkPermitStatus.WARNING
    return WorkPermitStatus.ACTIVE
