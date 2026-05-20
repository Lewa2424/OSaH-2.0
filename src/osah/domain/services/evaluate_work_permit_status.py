from datetime import datetime

from osah.domain.entities.work_permit_record import WorkPermitRecord
from osah.domain.entities.work_permit_status import WorkPermitStatus
from osah.domain.services.parse_storage_datetime_text import parse_storage_datetime_text


def evaluate_work_permit_status(
    work_permit_record: WorkPermitRecord,
    current_moment: datetime | None = None,
    warning_days: int = 3,
) -> WorkPermitStatus:
    """Оцінює статус наряду-допуску.
    Evaluates the work permit status.
    """

    if work_permit_record.reissued_to_record_id is not None and work_permit_record.canceled_at:
        return WorkPermitStatus.CANCELED
    if work_permit_record.canceled_at:
        return WorkPermitStatus.CANCELED
    if work_permit_record.closed_at:
        return WorkPermitStatus.CLOSED
    if not work_permit_record.responsible_person.strip():
        return WorkPermitStatus.INVALID

    reference_moment = current_moment or datetime.now()
    try:
        ends_at = parse_storage_datetime_text(work_permit_record.ends_at)
    except ValueError:
        return WorkPermitStatus.INVALID
    remaining_seconds = (ends_at - reference_moment).total_seconds()
    if remaining_seconds < 0:
        return WorkPermitStatus.EXPIRED
    if remaining_seconds <= warning_days * 24 * 60 * 60:
        return WorkPermitStatus.WARNING
    return WorkPermitStatus.ACTIVE
