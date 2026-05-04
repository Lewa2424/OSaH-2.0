from enum import StrEnum


class PpeProvisionStatus(StrEnum):
    """Статус обеспечения СИЗ.
    PPE provision status for a record.
    """

    REQUIRED_NOT_ISSUED = "required_not_issued"
    ISSUED = "issued"
    NOT_REQUIRED = "not_required"
    LEGACY_NOT_TRACKED = "legacy_not_tracked"
