from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.services.ai.compiler.compile_ai_command import compile_ai_command


def reconcile_ai_command_draft(draft: AiCommandDraft) -> AiCommandDraft:
    """Тимчасовий shim: делегує compile_ai_command.
    Temporary shim: delegates to compile_ai_command.
    """

    return compile_ai_command(draft).draft
