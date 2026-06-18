from enum import StrEnum


class AiSemanticMode(StrEnum):
    """Режим выполнения семантической AI-команды.
    Execution mode for a semantic AI command.
    """

    READ_ONLY = "read_only"
    DRAFT_ONLY = "draft_only"
    CONFIRM_THEN_EXECUTE = "confirm_then_execute"
    PREVIEW_THEN_CONFIRM = "preview_then_confirm"
    UNSUPPORTED = "unsupported"
