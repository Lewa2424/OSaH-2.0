from dataclasses import dataclass, field

from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_operation_plan_kind import AiOperationPlanKind
from osah.domain.entities.ai_semantic_mode import AiSemanticMode


@dataclass(frozen=True, slots=True)
class AiOperationPlan:
    """План безпечної обробки AI-команди для application/UI шару.
    Safe AI command handling plan for the application/UI layer.
    """

    kind: AiOperationPlanKind
    mode: AiSemanticMode
    draft: AiCommandDraft
    requires_confirmation: bool = False
    requires_preview: bool = False
    can_execute: bool = True
    issues: tuple[str, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)
