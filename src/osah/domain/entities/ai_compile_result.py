from dataclasses import dataclass, field

from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_pending_slot_kind import AiPendingSlotKind


@dataclass(slots=True, frozen=True)
class AiCompileResult:
    """Результат компіляції AI-команди.
    Result of compiling an AI command draft.
    """

    draft: AiCommandDraft
    missing_slots: tuple[AiPendingSlotKind, ...] = field(default_factory=tuple)
    needs_llm: bool = False
    session_prompt: str | None = None
