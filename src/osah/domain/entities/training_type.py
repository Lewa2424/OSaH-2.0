from enum import StrEnum


class TrainingType(StrEnum):
    """Типи інструктажів.
    Типы инструктажей.
    """

    INTRODUCTORY = "introductory"
    PRIMARY = "primary"
    REPEATED = "repeated"
    UNSCHEDULED = "unscheduled"
    TARGETED = "targeted"
