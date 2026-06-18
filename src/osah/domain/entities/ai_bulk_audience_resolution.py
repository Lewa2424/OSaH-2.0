from dataclasses import dataclass, field

from osah.domain.entities.ai_bulk_audience_resolution_status import AiBulkAudienceResolutionStatus
from osah.domain.entities.ai_bulk_audience_row import AiBulkAudienceRow
from osah.domain.entities.ai_bulk_audience_spec import AiBulkAudienceSpec
from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_entity_choice import AiEntityChoice


@dataclass(slots=True)
class AiBulkAudienceResolution:
    """Результат розв'язання аудиторії масової команди.
    Result of bulk audience resolution.
    """

    status: AiBulkAudienceResolutionStatus
    message: str = ""
    draft: AiCommandDraft | None = None
    rows: tuple[AiBulkAudienceRow, ...] = field(default_factory=tuple)
    personnel_numbers: tuple[str, ...] = field(default_factory=tuple)
    choices: tuple[AiEntityChoice, ...] = field(default_factory=tuple)
    pending_employee_query: str | None = None
    pending_registry_choice_kind: str | None = None
    updated_audience_spec: AiBulkAudienceSpec | None = None
