from osah.domain.entities.work_permit_record import WorkPermitRecord
from osah.domain.entities.work_permit_status import WorkPermitStatus


def build_work_permit_summary(work_permit_records: tuple[WorkPermitRecord, ...]) -> tuple[str, ...]:
    """Повертає короткі рядки для картки працівника по модулю нарядів-допусків.
    Returns short lines for the employee card in the work-permits module.
    """

    if not work_permit_records:
        return ("Активних нарядів-допусків поки немає.",)

    sorted_records = sorted(work_permit_records, key=lambda work_permit_record: work_permit_record.ends_at)
    return tuple(
        f"{work_permit_record.permit_number} | {_format_work_permit_status(work_permit_record.status)} | {work_permit_record.ends_at}"
        for work_permit_record in sorted_records[:3]
    )


def _format_work_permit_status(work_permit_status: WorkPermitStatus) -> str:
    """Повертає коротку локалізовану мітку статусу наряду-допуску.
    Returns a short localized work-permit status label.
    """

    if work_permit_status == WorkPermitStatus.ACTIVE:
        return "Активний"
    if work_permit_status == WorkPermitStatus.WARNING:
        return "Увага"
    if work_permit_status == WorkPermitStatus.EXPIRED:
        return "Прострочено"
    if work_permit_status in {WorkPermitStatus.CANCELED, WorkPermitStatus.REISSUED}:
        return "Скасовано"
    if work_permit_status == WorkPermitStatus.INVALID:
        return "Проблемний"
    return "Закрито"
