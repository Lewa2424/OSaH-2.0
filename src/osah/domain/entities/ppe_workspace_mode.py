from enum import StrEnum


class PpeWorkspaceMode(StrEnum):
    """Режим перегляду робочого простору ЗІЗ.
    PPE workspace view mode.
    """

    BY_RECORDS = "by_records"
    BY_EMPLOYEES = "by_employees"
