from datetime import date

from osah.domain.entities.medical_record import MedicalRecord
from osah.domain.entities.medical_status import MedicalStatus
from osah.domain.services.format_ui_date import format_ui_date


# ###### ПРИЧИНА СТАТУСУ МЕДИЦИНИ / BUILD MEDICAL STATUS REASON ######
def build_medical_status_reason(medical_record: MedicalRecord, today: date | None = None) -> str:
    """Пояснює, чому меддопуск має конкретний статус.
    Explains why a medical admission has a specific status.
    """

    current_date = today or date.today()
    remaining_days = (date.fromisoformat(medical_record.valid_until) - current_date).days
    if medical_record.status == MedicalStatus.EXPIRED:
        return "Не допущено - строк меддопуску минув"
    if medical_record.status == MedicalStatus.NOT_FIT:
        return "Не допущено - медичне рішення забороняє роботи"
    if medical_record.status == MedicalStatus.RESTRICTED:
        return "Обмежено - заборонені окремі види робіт"
    if medical_record.status == MedicalStatus.WARNING:
        return f"Увага - меддопуск спливає через {remaining_days} дн."
    return f"Допущено - строк дії до {format_ui_date(medical_record.valid_until)}"
