from datetime import datetime

from osah.domain.entities.work_permit_record import WorkPermitRecord
from osah.domain.entities.work_permit_status import WorkPermitStatus
from osah.domain.services.format_ui_datetime import format_ui_datetime
from osah.domain.services.parse_storage_datetime_text import parse_storage_datetime_text


def build_work_permit_status_reason(work_permit_record: WorkPermitRecord) -> str:
    """Повертає пояснення статусу наряду.
    Returns a human-readable permit status reason.
    """

    if work_permit_record.status == WorkPermitStatus.CANCELED:
        if work_permit_record.reissued_to_record_id is not None:
            reason_text = work_permit_record.reissue_reason_text or work_permit_record.cancel_reason_text or "не вказано"
            return (
                f"Скасовано - на основі цього запису створено новий наряд #{work_permit_record.reissued_to_record_id}. "
                f"Причина: {reason_text}"
            )
        return f"Скасовано - {work_permit_record.cancel_reason_text or 'причину не вказано'}"
    if work_permit_record.status == WorkPermitStatus.CLOSED:
        return f"Закрито вручну {format_ui_datetime(work_permit_record.closed_at or '')}"
    if work_permit_record.status == WorkPermitStatus.INVALID:
        if not work_permit_record.responsible_person.strip():
            return "Проблемний стан - не вказано керівника робіт"
        return "Проблемний стан - у наряді вказано некоректну дату або час"
    if work_permit_record.status == WorkPermitStatus.EXPIRED:
        if work_permit_record.extension_count > 0:
            return f"Критично - продовжений строк дії минув {format_ui_datetime(work_permit_record.ends_at)}, наряд не закрито"
        return f"Критично - строк дії минув {format_ui_datetime(work_permit_record.ends_at)}, наряд не закрито"
    if work_permit_record.status == WorkPermitStatus.WARNING:
        try:
            days = max(0, (parse_storage_datetime_text(work_permit_record.ends_at) - datetime.now()).days)
        except ValueError:
            return "Проблемний стан - у наряді вказано некоректну дату або час"
        if work_permit_record.extension_count > 0:
            return f"Увага - продовжений строк дії спливає через {days} дн."
        return f"Увага - строк дії спливає через {days} дн."
    if work_permit_record.extension_count > 0:
        return f"Діє - наряд продовжено до {format_ui_datetime(work_permit_record.ends_at)}"
    return f"Діє - строк до {format_ui_datetime(work_permit_record.ends_at)}"
