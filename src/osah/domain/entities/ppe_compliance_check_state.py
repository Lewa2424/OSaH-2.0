from enum import StrEnum


class PpeComplianceCheckState(StrEnum):
    """Состояние проверки соответствия СИЗ.
    PPE compliance-check tracking state.
    """

    CHECKED = "checked"
    NOT_CHECKED = "not_checked"
    LEGACY_NOT_TRACKED = "legacy_not_tracked"
