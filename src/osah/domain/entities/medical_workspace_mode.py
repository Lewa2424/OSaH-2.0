from enum import StrEnum


class MedicalWorkspaceMode(StrEnum):
    """Режим перегляду робочого простору медицини.
    Medical workspace view mode.
    """

    BY_RECORDS = "by_records"
    BY_EMPLOYEES = "by_employees"
