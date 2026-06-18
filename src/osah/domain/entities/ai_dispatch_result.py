from dataclasses import dataclass, field

from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_dispatch_result_kind import AiDispatchResultKind
from osah.domain.entities.ai_entity_choice import AiEntityChoice
from osah.domain.entities.ai_navigation_target import AiNavigationTarget


@dataclass(slots=True)
class AiDispatchResult:
    """Результат application-level маршрутизации AI-команды.
    Application-level dispatch result for a parsed AI command.
    """

    kind: AiDispatchResultKind
    draft: AiCommandDraft | None = None
    message: str = ""
    answer_text: str = ""
    follow_up_navigation: AiNavigationTarget | None = None
    navigation_target: AiNavigationTarget | None = None
    allow_copy: bool = False
    choices: tuple[AiEntityChoice, ...] = field(default_factory=tuple)
    pending_ppe_item_index: int | None = None
    pending_answer_mode: bool = False
