from enum import StrEnum


class WorkPermitTargetTrainingStatus(StrEnum):
    """Стан цільового інструктажу для наряду-допуску.
    Targeted-training state for a work permit.
    """

    LEGACY_NOT_TRACKED = "legacy_not_tracked"
    NOT_DONE = "not_done"
    DONE_PASSED = "done_passed"
    DONE_FAILED = "done_failed"

    UNKNOWN = "unknown"
    NOT_REQUIRED = "not_required"
    REQUIRED_NOT_DONE = "required_not_done"
    DONE = "done"
