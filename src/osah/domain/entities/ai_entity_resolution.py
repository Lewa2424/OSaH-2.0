from dataclasses import dataclass, field

from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_entity_choice import AiEntityChoice
from osah.domain.entities.ai_entity_resolution_status import AiEntityResolutionStatus


@dataclass(slots=True)
class AiEntityResolution:
    """Результат розв'язання сутностей після парсингу команди.
    Result of entity resolution after command parsing.
    """

    status: AiEntityResolutionStatus
    message: str = ""
    draft: AiCommandDraft | None = None
    choices: tuple[AiEntityChoice, ...] = field(default_factory=tuple)
    resolved_personnel_number: str | None = None
    pending_ppe_item_index: int | None = None
