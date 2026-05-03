from datetime import date

from osah.domain.entities.training_work_risk_category import TrainingWorkRiskCategory
from osah.domain.services.add_months_to_date import add_months_to_date


# ###### РАСЧЁТ СЛЕДУЮЩЕГО ПОВТОРНОГО ИНСТРУКТАЖА / CALCULATE NEXT REPEATED TRAINING ######
def calculate_next_training_control_date(
    event_date: date,
    work_risk_category: TrainingWorkRiskCategory,
) -> date:
    """Возвращает дату следующего повторного инструктажа по категории работ.
    Returns the next repeated training date based on the work category.
    """

    if work_risk_category == TrainingWorkRiskCategory.HIGH_RISK:
        return add_months_to_date(event_date, 3)
    if work_risk_category == TrainingWorkRiskCategory.REGULAR:
        return add_months_to_date(event_date, 6)
    raise ValueError("Для расчёта следующего повторного инструктажа нужно выбрать категорию работ.")
