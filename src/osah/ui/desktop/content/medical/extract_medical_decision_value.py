from osah.domain.entities.medical_decision import MedicalDecision
from osah.domain.services.format_medical_decision_label import format_medical_decision_label


# ###### ВИДІЛЕННЯ ЗНАЧЕННЯ МЕДИЧНОГО РІШЕННЯ / ВЫДЕЛЕНИЕ ЗНАЧЕНИЯ МЕДИЦИНСКОГО РЕШЕНИЯ ######
def extract_medical_decision_value(medical_decision_label: str) -> str:
    """Повертає технічне значення медичного рішення за локалізованим підписом.
    Возвращает техническое значение медицинского решения по локализованной подписи.
    """

    for medical_decision in MedicalDecision:
        if format_medical_decision_label(medical_decision) == medical_decision_label:
            return medical_decision.value
    return ""
