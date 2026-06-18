from enum import StrEnum


class AiSemanticModule(StrEnum):
    """Раздел ClearWork, к которому относится AI-команда.
    ClearWork module targeted by an AI command.
    """

    EMPLOYEES = "employees"
    TRAININGS = "trainings"
    PPE = "ppe"
    MEDICAL = "medical"
    WORK_PERMITS = "work_permits"
    REPORTS = "reports"
    UNKNOWN = "unknown"
