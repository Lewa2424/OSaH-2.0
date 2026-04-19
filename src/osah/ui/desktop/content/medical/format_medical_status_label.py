from osah.domain.entities.medical_status import MedicalStatus


# ###### ФОРМАТУВАННЯ СТАТУСУ МЕДИЦИНИ / ФОРМАТИРОВАНИЕ СТАТУСА МЕДИЦИНЫ ######
def format_medical_status_label(medical_status: MedicalStatus) -> str:
    """Повертає локалізовану мітку статусу медицини для UI.
    Возвращает локализованную метку статуса медицины для UI.
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
