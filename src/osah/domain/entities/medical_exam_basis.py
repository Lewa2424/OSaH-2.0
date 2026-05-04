from enum import StrEnum


class MedicalExamBasis(StrEnum):
    """Основание обязательности медосмотра.
    Basis for mandatory medical examination.
    """

    HARMFUL_OR_DANGEROUS_FACTORS = "harmful_or_dangerous_factors"
    HEAVY_WORK = "heavy_work"
    PROFESSIONAL_SELECTION = "professional_selection"
    UNDER_21 = "under_21"
    INTERNAL_LIST = "internal_list"
    OTHER = "other"
    LEGACY_NOT_TRACKED = "legacy_not_tracked"
