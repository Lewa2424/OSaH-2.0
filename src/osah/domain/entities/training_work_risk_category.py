from enum import StrEnum


class TrainingWorkRiskCategory(StrEnum):
    """Категория работ для расчёта следующего повторного инструктажа.
    Work category used to calculate the next repeated training date.
    """

    NOT_APPLICABLE = "not_applicable"
    REGULAR = "regular"
    HIGH_RISK = "high_risk"
