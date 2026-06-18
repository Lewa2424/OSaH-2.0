from enum import StrEnum


class AiCommandResolutionStatus(StrEnum):
    """Статус обробки команди AI.
    AI command processing status.
    """

    PARSED = "parsed"
    NEEDS_CLARIFICATION = "needs_clarification"
    INVALID_DRAFT = "invalid_draft"
    ACCESS_DENIED = "access_denied"
    RUNTIME_UNAVAILABLE = "runtime_unavailable"
    LLM_UNAVAILABLE = "llm_unavailable"
    ANSWER_READY = "answer_ready"
