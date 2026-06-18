from dataclasses import dataclass, field

from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_confirmation_view import AiConfirmationView
from osah.domain.entities.ai_entity_choice import AiEntityChoice
from osah.domain.entities.ai_prepared_command_status import AiPreparedCommandStatus


@dataclass(slots=True)
class AiPreparedWriteCommand:
    """Подготовленная одиночная AI-команда для UI-подтверждения.
    Prepared single AI command for UI confirmation.
    """

    status: AiPreparedCommandStatus
    draft: AiCommandDraft
    message: str = ""
    choices: tuple[AiEntityChoice, ...] = field(default_factory=tuple)
    pending_ppe_item_index: int | None = None
    personnel_number: str | None = None
    confirmation_view: AiConfirmationView | None = None
