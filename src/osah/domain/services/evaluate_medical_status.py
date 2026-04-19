from datetime import date

from osah.domain.entities.medical_decision import MedicalDecision
from osah.domain.entities.medical_record import MedicalRecord
from osah.domain.entities.medical_status import MedicalStatus


# ###### ОЦІНКА СТАТУСУ МЕДДОПУСКУ / ОЦЕНКА СТАТУСА МЕДДОПУСКА ######
def evaluate_medical_status(
    medical_record: MedicalRecord,
    today: date | None = None,
    warning_days: int = 7,
) -> MedicalStatus:
    """Повертає статус медичного запису за строком і рішенням допуску.
    Возвращает статус медицинской записи по сроку и решению допуска.
    """

    current_date = today or date.today()
    valid_until = date.fromisoformat(medical_record.valid_until)
    remaining_days = (valid_until - current_date).days
    if remaining_days < 0:
        return MedicalStatus.EXPIRED
    if medical_record.medical_decision == MedicalDecision.NOT_FIT:
        return MedicalStatus.NOT_FIT
    if medical_record.medical_decision == MedicalDecision.RESTRICTED:
        return MedicalStatus.RESTRICTED
    if remaining_days <= warning_days:
        return MedicalStatus.WARNING
    return MedicalStatus.CURRENT
