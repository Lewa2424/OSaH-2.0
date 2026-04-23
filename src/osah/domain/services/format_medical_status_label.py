from osah.domain.entities.medical_status import MedicalStatus


# ###### ФОРМАТУВАННЯ СТАТУСУ МЕДИЦИНИ / FORMAT MEDICAL STATUS ######
def format_medical_status_label(status: MedicalStatus) -> str:
    """Повертає україномовну назву статусу меддопуску.
    Returns a Ukrainian medical status label.
    """

    if status == MedicalStatus.CURRENT:
        return "Допущено"
    if status == MedicalStatus.WARNING:
        return "Увага"
    if status == MedicalStatus.RESTRICTED:
        return "Обмежено"
    if status == MedicalStatus.EXPIRED:
        return "Не допущено"
    return "Не допущено"
