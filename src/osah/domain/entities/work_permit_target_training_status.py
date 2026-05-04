from enum import StrEnum


class WorkPermitTargetTrainingStatus(StrEnum):
    """Состояние целевого инструктажа для наряда-допуска.
    Targeted-training state for a work permit.
    """

    UNKNOWN = "unknown"
    NOT_REQUIRED = "not_required"
    REQUIRED_NOT_DONE = "required_not_done"
    DONE = "done"
    LEGACY_NOT_TRACKED = "legacy_not_tracked"
