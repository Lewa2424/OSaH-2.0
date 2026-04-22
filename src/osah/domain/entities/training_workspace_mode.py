from enum import StrEnum


class TrainingWorkspaceMode(StrEnum):
    """Режим перегляду робочого простору інструктажів.
    Trainings workspace view mode.
    """

    BY_RECORDS = "by_records"
    BY_EMPLOYEES = "by_employees"
