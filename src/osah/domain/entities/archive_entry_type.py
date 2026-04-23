from enum import StrEnum


class ArchiveEntryType(StrEnum):
    """Archive record kinds available in the archive registry."""

    EMPLOYEE = "employee"
    WORK_PERMIT = "work_permit"
