import json
import re
from pathlib import Path

from osah.application.services.ai.build_ai_registry_hints import build_ai_registry_hints
from osah.application.services.ai.build_ai_unified_system_prompt import is_write_command_text
from osah.domain.entities.ai_dialogue_state import AiDialogueState
from osah.domain.entities.ai_ui_context import AiUiContext
from osah.domain.services.ai.serialize_ai_dialogue_state_for_prompt import serialize_ai_dialogue_state_for_prompt

_MAX_DIALOGUE_CONTEXT_CHARS = 1200
_MAX_UI_CONTEXT_CHARS = 600
_REGISTRY_HINT_MARKERS = re.compile(
    r"(?:"
    r"в\s+подраздел|подразделени|"
    r"служб|"
    r"из\s+водит|водител|"
    r"стропальник|навантажувач|посад|"
    r"кто\s+работает|хто\s+працює|кому\s+нужн|кому\s+потрібн"
    r")",
    re.IGNORECASE,
)
_WRITE_DEPT_MARKER = re.compile(
    r"(?:подразделени|підрозділ|отдел|дільниц|участк|цех|служб)",
    re.IGNORECASE,
)


def command_needs_registry_hints(command_text: str) -> bool:
    """Перевіряє, чи варто додавати підказки реєстру в LLM prompt.
    Checks whether registry hints should be added to the LLM prompt.
    """

    return _REGISTRY_HINT_MARKERS.search(command_text.strip()) is not None


def should_attach_registry_hints(command_text: str) -> bool:
    """Чи додавати registry hints: read-запити так, write з явним dept — ні.
    Whether to attach registry hints: yes for read queries, no for write with explicit dept.
    """

    normalized = command_text.strip()
    if not normalized:
        return False
    if is_write_command_text(normalized) and _WRITE_DEPT_MARKER.search(normalized):
        return False
    return command_needs_registry_hints(normalized)


def build_ai_llm_user_prompt(
    command_text: str,
    *,
    dialogue_state: AiDialogueState | None = None,
    ui_context: AiUiContext | None = None,
    database_path: Path | None = None,
) -> str:
    """Збирає user prompt для LLM з командою та контекстом діалогу/UI.
    Builds an LLM user prompt from the command and dialogue/UI context.
    """

    blocks: list[str] = []

    dialogue_json = serialize_ai_dialogue_state_for_prompt(dialogue_state)
    if dialogue_json:
        if len(dialogue_json) > _MAX_DIALOGUE_CONTEXT_CHARS:
            dialogue_json = dialogue_json[:_MAX_DIALOGUE_CONTEXT_CHARS] + "…"
        blocks.append("[dialogue_context]\n" + dialogue_json)

    if ui_context is not None:
        ui_payload = {
            "section": ui_context.section.value if ui_context.section else None,
            "employee_personnel_number": ui_context.employee_personnel_number,
            "focused_field_key": ui_context.focused_field_key,
            "active_dialog": ui_context.active_dialog,
        }
        ui_json = json.dumps(ui_payload, ensure_ascii=False, separators=(",", ":"))
        if len(ui_json) > _MAX_UI_CONTEXT_CHARS:
            ui_json = ui_json[:_MAX_UI_CONTEXT_CHARS] + "…"
        blocks.append("[ui_context]\n" + ui_json)

    if database_path is not None and should_attach_registry_hints(command_text):
        blocks.append("[registry_hints]\n" + build_ai_registry_hints(database_path))

    blocks.append("[command]\n" + command_text.strip())
    return "\n\n".join(blocks)
