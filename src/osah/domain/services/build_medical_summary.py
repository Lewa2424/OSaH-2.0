from osah.domain.entities.medical_record import MedicalRecord
from osah.domain.entities.medical_status import MedicalStatus


# ###### ПОБУДОВА ЗВЕДЕННЯ МЕДИЦИНИ / ПОСТРОЕНИЕ СВОДКИ МЕДИЦИНЫ ######
def build_medical_summary(medical_records: tuple[MedicalRecord, ...]) -> tuple[str, ...]:
    """Повертає короткі рядки для картки працівника по модулю медицини.
    Возвращает короткие строки для карточки сотрудника по модулю медицины.
    """

    if not medical_records:
        return ("Медичних записів поки немає.",)

    sorted_records = sorted(medical_records, key=lambda medical_record: medical_record.valid_until)
    return tuple(
        f"{medical_record.valid_until} | {_format_medical_status(medical_record.status)}"
        for medical_record in sorted_records[:3]
    )


# ###### ФОРМАТУВАННЯ СТАТУСУ МЕДИЦИНИ / ФОРМАТИРОВАНИЕ СТАТУСА МЕДИЦИНЫ ######
def _format_medical_status(medical_status: MedicalStatus) -> str:
    """Повертає коротку локалізовану мітку статусу медицини.
    Возвращает краткую локализованную метку статуса медицины.
    """

    if medical_status == MedicalStatus.CURRENT:
        return "Актуально"
    if medical_status == MedicalStatus.WARNING:
        return "Увага"
    if medical_status == MedicalStatus.EXPIRED:
        return "Прострочено"
    if medical_status == MedicalStatus.RESTRICTED:
        return "Обмеження"
    return "Не допущено"
