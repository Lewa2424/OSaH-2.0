from dataclasses import dataclass, field

from osah.domain.entities.ai_bulk_confirmation_view import AiBulkConfirmationView
from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_entity_choice import AiEntityChoice
from osah.domain.entities.ai_prepared_command_status import AiPreparedCommandStatus


@dataclass(slots=True)
class AiPreparedBulkCommand:
    """Подготовленная массовая AI-команда для preview и подтверждения.
    Prepared bulk AI command for preview and confirmation.
    """

    status: AiPreparedCommandStatus
    draft: AiCommandDraft
    message: str = ""
    choices: tuple[AiEntityChoice, ...] = field(default_factory=tuple)
    pending_employee_query: str | None = None
    pending_registry_choice_kind: str | None = None
    personnel_numbers: tuple[str, ...] = field(default_factory=tuple)
    confirmation_view: AiBulkConfirmationView | None = None
