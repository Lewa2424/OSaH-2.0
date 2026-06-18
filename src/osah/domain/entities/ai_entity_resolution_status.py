from enum import StrEnum


class AiEntityResolutionStatus(StrEnum):
    """Статус розв'язання сутностей AI-команди.
    Entity resolution status for an AI command.
    """

    READY = "ready"
    NEEDS_CLARIFICATION = "needs_clarification"
    NOT_FOUND = "not_found"
