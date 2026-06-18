from enum import StrEnum


class AiBulkAudienceResolutionStatus(StrEnum):
    """Статус розв'язання аудиторії масової команди.
    Bulk audience resolution status.
    """

    READY = "ready"
    EMPTY = "empty"
    TOO_LARGE = "too_large"
    NEEDS_CLARIFICATION = "needs_clarification"
