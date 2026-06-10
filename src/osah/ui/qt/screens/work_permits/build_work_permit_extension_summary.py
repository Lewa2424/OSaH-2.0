from osah.domain.entities.work_permit_record import WorkPermitRecord
from osah.domain.entities.work_permit_status import WorkPermitStatus
from osah.domain.services.format_ui_datetime import format_ui_datetime


def build_work_permit_extension_summary(work_permit_record: WorkPermitRecord | None) -> dict[str, object]:
    """Повертає тексти та прапорці для блоку строку дії наряду в Qt.
    Returns texts and flags for the work-permit term block in Qt.
    """

    if work_permit_record is None:
        return {
            "base_term_text": "Базовий строк: задається під час створення",
            "current_term_text": "Поточний строк: ще не визначено",
            "state_text": "Продовження буде доступне після збереження наряду.",
            "reason_text": "Причина продовження: -",
            "notice_text": "Під час створення задайте базовий строк не більше 15 календарних днів.",
            "can_extend": False,
            "lock_dates": False,
        }

    base_ends_at = work_permit_record.base_ends_at or work_permit_record.ends_at
    if work_permit_record.closed_at:
        state_text = "Наряд закрито. Продовження строку недоступне."
        can_extend = False
    elif work_permit_record.canceled_at:
        state_text = "Наряд скасовано. Продовження строку недоступне."
        can_extend = False
    elif work_permit_record.extension_count > 0:
        extension_marker = format_ui_datetime(work_permit_record.extended_at or "")
        state_text = (
            f"Наряд вже продовжено один раз {extension_marker}."
            if extension_marker
            else "Наряд вже продовжено один раз."
        )
        can_extend = False
    elif work_permit_record.status in {WorkPermitStatus.ACTIVE, WorkPermitStatus.WARNING}:
        state_text = "Доступне одноразове продовження ще до 15 календарних днів."
        can_extend = True
    elif work_permit_record.status == WorkPermitStatus.EXPIRED:
        state_text = "Строк дії вже сплив. Наряд можна продовжити один раз або закрити."
        can_extend = True
    else:
        state_text = "Продовження недоступне для поточного стану наряду."
        can_extend = False

    if work_permit_record.extension_count > 0:
        notice_text = (
            "Дати після продовження не змінюються вручну — лише кнопкою «Продовжити наряд». "
            "Цільовий інструктаж і примітки можна зберігати звичайно."
        )
    else:
        notice_text = (
            "Строк дії змінюється кнопкою «Продовжити наряд», а не ручним редагуванням полів дат."
        )

    return {
        "base_term_text": f"Базовий строк: до {format_ui_datetime(base_ends_at)}",
        "current_term_text": f"Поточний строк: до {format_ui_datetime(work_permit_record.ends_at)}",
        "state_text": state_text,
        "reason_text": f"Причина продовження: {work_permit_record.extension_reason_text or '-'}",
        "notice_text": notice_text,
        "can_extend": can_extend,
        "lock_dates": True,
    }
