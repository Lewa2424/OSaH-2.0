from dataclasses import dataclass, field

from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_entity_choice import AiEntityChoice


@dataclass(slots=True)
class AiGroundingResult:
    """Результат DB-grounding для AI-чернетки.
    Result of DB grounding for an AI command draft.
    """

    ok: bool
    draft: AiCommandDraft
    message: str = ""
    choices: tuple[AiEntityChoice, ...] = field(default_factory=tuple)
    choice_kind: str | None = None
