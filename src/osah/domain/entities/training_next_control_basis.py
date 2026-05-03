from enum import StrEnum


class TrainingNextControlBasis(StrEnum):
    """Основание, по которому определена следующая контрольная дата инструктажа.
    Basis used to define the next training control date.
    """

    MANUAL = "manual"
    REQUIRES_PRIMARY_AFTER_INTRODUCTORY = "requires_primary_after_introductory"
    INTRODUCTORY_PRIMARY_NOT_REQUIRED = "introductory_primary_not_required"
    CALCULATED_AFTER_PRIMARY_3M = "calculated_after_primary_3m"
    CALCULATED_AFTER_PRIMARY_6M = "calculated_after_primary_6m"
    CALCULATED_AFTER_REPEATED_3M = "calculated_after_repeated_3m"
    CALCULATED_AFTER_REPEATED_6M = "calculated_after_repeated_6m"
    RECALCULATED_AFTER_UNSCHEDULED_3M = "recalculated_after_unscheduled_3m"
    RECALCULATED_AFTER_UNSCHEDULED_6M = "recalculated_after_unscheduled_6m"
    RECALCULATED_AFTER_TARGETED_3M = "recalculated_after_targeted_3m"
    RECALCULATED_AFTER_TARGETED_6M = "recalculated_after_targeted_6m"
    DOES_NOT_CHANGE_REPEATED_CONTROL = "does_not_change_repeated_control"
