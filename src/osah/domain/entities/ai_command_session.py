from dataclasses import dataclass, field

from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_pending_slot_kind import AiPendingSlotKind


@dataclass(slots=True)
class AiCommandSession:
    """Активна сесія уточнення слотів AI-команди.
    Active slot-filling session for an AI command.
    """

    draft: AiCommandDraft
    missing_slots: tuple[AiPendingSlotKind, ...] = field(default_factory=tuple)
    prompt_message: str = ""
    trace_id: str | None = None
    pending_ppe_item_index: int | None = None
    pending_bulk_employee_query: str | None = None
    answer_mode: bool = False
