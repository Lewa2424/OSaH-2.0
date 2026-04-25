from datetime import date

from osah.domain.entities.ppe_record import PpeRecord
from osah.domain.entities.ppe_status import PpeStatus
from osah.domain.services.format_ui_date import format_ui_date


# ###### ПРИЧИНА СТАТУСУ ЗІЗ / BUILD PPE STATUS REASON ######
def build_ppe_status_reason(ppe_record: PpeRecord, today: date | None = None) -> str:
    """Пояснює, чому позиція ЗІЗ має конкретний статус.
    Explains why a PPE item has a specific status.
    """

    if ppe_record.status == PpeStatus.NOT_ISSUED:
        return f"Критично - {ppe_record.ppe_name} не видано"
    current_date = today or date.today()
    remaining_days = (date.fromisoformat(ppe_record.replacement_date) - current_date).days
    if ppe_record.status == PpeStatus.EXPIRED:
        return f"Критично - строк {ppe_record.ppe_name} минув"
    if ppe_record.status == PpeStatus.WARNING:
        return f"Увага - заміна через {remaining_days} дн."
    if not ppe_record.is_required and ppe_record.is_issued:
        return f"Несистемно - {ppe_record.ppe_name} видано без ознаки обов'язковості"
    return f"Актуально - кількість {ppe_record.quantity}, заміна до {format_ui_date(ppe_record.replacement_date)}"
