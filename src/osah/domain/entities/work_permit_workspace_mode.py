from enum import StrEnum


class WorkPermitWorkspaceMode(StrEnum):
    """Режими перегляду Qt-модуля нарядів-допусків.
    View modes for the Qt work permits module.
    """

    BY_PERMITS = "by_permits"
    BY_EMPLOYEES = "by_employees"
    ACTIVE_WORKS = "active_works"
