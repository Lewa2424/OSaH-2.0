from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_navigation_target import AiNavigationTarget
from osah.domain.entities.ai_ui_context import AiUiContext
from osah.domain.services.ai.build_ai_navigation_target import build_ai_navigation_target
from osah.domain.services.ai.ensure_ai_intent_is_allowed import is_ai_navigation_intent


def build_ai_read_navigation_target(
    draft: AiCommandDraft,
    *,
    ui_context: AiUiContext | None = None,
) -> AiNavigationTarget | None:
    """Повертає ціль read-only навігації для AI-команди.
    Returns a read-only navigation target for an AI command.
    """

    if not is_ai_navigation_intent(draft.intent):
        return None
    return build_ai_navigation_target(draft, ui_context=ui_context)
