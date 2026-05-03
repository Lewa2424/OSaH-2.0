from osah.domain.entities.training_work_risk_category import TrainingWorkRiskCategory


# ###### ФОРМАТ КАТЕГОРІЇ РОБІТ ІНСТРУКТАЖУ / FORMAT TRAINING WORK RISK CATEGORY ######
def format_training_work_risk_category_label(
    work_risk_category: TrainingWorkRiskCategory,
) -> str:
    """Повертає зрозумілу назву категорії робіт для інструктажу.
    Returns a readable work category label for a training record.
    """

    if work_risk_category == TrainingWorkRiskCategory.HIGH_RISK:
        return "Роботи підвищеної небезпеки"
    if work_risk_category == TrainingWorkRiskCategory.REGULAR:
        return "Звичайні роботи"
    return "Не застосовується"
