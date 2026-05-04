from enum import StrEnum


class TrainingWorkAdmissionStatus(StrEnum):
    """Статус допуска к работе после инструктажа.
    Work-admission status after a training event.
    """

    ALLOWED = "allowed"
    NOT_ALLOWED = "not_allowed"
    NOT_APPLICABLE = "not_applicable"
    LEGACY_NOT_TRACKED = "legacy_not_tracked"
