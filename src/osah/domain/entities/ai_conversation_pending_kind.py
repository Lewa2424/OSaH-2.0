from enum import StrEnum


class AiConversationPendingKind(StrEnum):
    """Тип очікуваного уточнення в межах AI-діалогу.
    Pending clarification kind within an AI dialogue.
    """

    DEPARTMENT_EMPLOYEES = "department_employees"
