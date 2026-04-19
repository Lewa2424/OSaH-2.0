from osah.domain.entities.medical_decision import MedicalDecision


# ###### ФОРМАТУВАННЯ РІШЕННЯ МЕДДОПУСКУ / ФОРМАТИРОВАНИЕ РЕШЕНИЯ МЕДДОПУСКА ######
def format_medical_decision_label(medical_decision: MedicalDecision) -> str:
    """Повертає локалізовану мітку рішення меддопуску.
    Возвращает локализованную метку решения меддопуска.
    """

    if medical_decision == MedicalDecision.FIT:
        return "Допущено"
    if medical_decision == MedicalDecision.RESTRICTED:
        return "Допущено з обмеженнями"
    return "Не допущено"
