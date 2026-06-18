from enum import StrEnum


class AiPreparedCommandStatus(StrEnum):
    """Статус подготовки AI-команды перед UI-подтверждением.
    Preparation status for an AI command before UI confirmation.
    """

    READY = "ready"
    NEEDS_CLARIFICATION = "needs_clarification"
    NOT_FOUND = "not_found"
    INVALID = "invalid"
