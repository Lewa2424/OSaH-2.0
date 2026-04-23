from datetime import datetime

from osah.domain.entities.work_permit_record import WorkPermitRecord
from osah.domain.entities.work_permit_status import WorkPermitStatus


# ###### ПРИЧИНА СТАТУСУ НАРЯДУ / WORK PERMIT STATUS REASON ######
def build_work_permit_status_reason(work_permit_record: WorkPermitRecord) -> str:
    """Повертає людську причину поточного статусу наряду-допуску.
    Returns a human-readable reason for the current work permit status.
    """

    if work_permit_record.status == WorkPermitStatus.CANCELED:
        return f"Скасовано - {work_permit_record.cancel_reason_text or 'причину не вказано'}"
    if work_permit_record.status == WorkPermitStatus.CLOSED:
        return f"Закрито вручну {work_permit_record.closed_at}"
    if work_permit_record.status == WorkPermitStatus.INVALID:
        return "Проблемний - відсутній відповідальний, допускаючий або учасники"
    if work_permit_record.status == WorkPermitStatus.EXPIRED:
        return f"Критично - строк дії минув {work_permit_record.ends_at}, наряд не закрито"
    if work_permit_record.status == WorkPermitStatus.WARNING:
        days = max(0, (datetime.fromisoformat(work_permit_record.ends_at) - datetime.now()).days)
        return f"Увага - строк дії спливає через {days} дн."
    return f"Діє - строк до {work_permit_record.ends_at}"
