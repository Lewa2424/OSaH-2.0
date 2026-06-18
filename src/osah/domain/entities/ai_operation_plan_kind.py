from enum import StrEnum


class AiOperationPlanKind(StrEnum):
    """Тип маршрута виконання AI-команди.
    Execution route type for an AI command.
    """

    NAVIGATION = "navigation"
    ANSWER = "answer"
    SINGLE_WRITE = "single_write"
    BULK_WRITE = "bulk_write"
    UNSUPPORTED = "unsupported"
