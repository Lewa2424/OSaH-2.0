from enum import StrEnum


class MedicalDecision(StrEnum):
    """Рішення меддопуску.
    Решения меддопуска.
    """

    FIT = "fit"
    RESTRICTED = "restricted"
    NOT_FIT = "not_fit"
