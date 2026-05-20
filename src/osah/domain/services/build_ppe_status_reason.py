from datetime import date

from osah.domain.entities.ppe_compliance_check_state import PpeComplianceCheckState
from osah.domain.entities.ppe_provision_status import PpeProvisionStatus
from osah.domain.entities.ppe_record import PpeRecord
from osah.domain.entities.ppe_status import PpeStatus
from osah.domain.services.format_ui_date import format_ui_date
from osah.domain.services.parse_storage_date_text import parse_storage_date_text


# ###### ПРИЧИНА СТАТУСА СИЗ / BUILD PPE STATUS REASON ######
def build_ppe_status_reason(ppe_record: PpeRecord, today: date | None = None) -> str:
    """Объясняет, почему позиция СИЗ имеет конкретный статус.
    Explains why a PPE item has a specific status.
    """

    if ppe_record.provision_status == PpeProvisionStatus.NOT_REQUIRED:
        return "Не требуется по текущим условиям работ"
    if ppe_record.status == PpeStatus.NOT_ISSUED:
        return f"Критично - {ppe_record.ppe_name} положено, но не выдано"
    current_date = today or date.today()
    try:
        remaining_days = (parse_storage_date_text(ppe_record.replacement_date) - current_date).days
    except ValueError:
        return f"Критично - у записі ЗІЗ {ppe_record.ppe_name} вказано некоректну дату заміни"
    if ppe_record.status == PpeStatus.EXPIRED:
        return f"Критично - срок использования {ppe_record.ppe_name} истек"
    if ppe_record.status == PpeStatus.WARNING:
        return f"Увага - заміна через {remaining_days} дн."
    if ppe_record.compliance_check_state == PpeComplianceCheckState.NOT_CHECKED:
        return "Увага - відповідність ЗІЗ умовам роботи не підтверджена"
    return f"Актуально - кількість {ppe_record.quantity}, заміна до {format_ui_date(ppe_record.replacement_date)}"
