from osah.domain.entities.medical_decision import MedicalDecision
from osah.domain.services.format_medical_decision_label import format_medical_decision_label


# ###### ПОБУДОВА ОПЦІЙ МЕДИЧНОГО РІШЕННЯ / ПОСТРОЕНИЕ ОПЦИЙ МЕДИЦИНСКОГО РЕШЕНИЯ ######
def build_medical_decision_options() -> tuple[str, ...]:
    """Повертає локалізовані підписи медичних рішень для форми.
    Возвращает локализованные подписи медицинских решений для формы.
    """

    return tuple(format_medical_decision_label(medical_decision) for medical_decision in MedicalDecision)
