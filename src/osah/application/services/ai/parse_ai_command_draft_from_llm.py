from pathlib import Path

from osah.application.services.ai.build_ai_unified_system_prompt import build_ai_unified_system_prompt
from osah.application.services.ai.build_ai_llm_user_prompt import build_ai_llm_user_prompt
from osah.domain.entities.ai_dialogue_state import AiDialogueState
from osah.domain.entities.ai_runtime_paths import AiRuntimePaths
from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.entities.ai_ui_context import AiUiContext
from osah.domain.services.ai.extract_json_object_from_llm_text import extract_json_object_from_llm_text
from osah.domain.services.ai.map_ai_payload_to_draft import map_ai_payload_to_draft
from osah.domain.services.ai.semantic.adapt_semantic_draft_to_command_draft import (
    adapt_semantic_draft_to_command_draft,
)
from osah.domain.services.ai.semantic.map_ai_semantic_payload_to_draft import map_ai_semantic_payload_to_draft
from osah.infrastructure.ai.llama_server_session import ensure_llama_server_running
from osah.infrastructure.ai.request_llama_chat_completion import (
    LlamaServerHttpError,
    request_llama_chat_completion,
)
from osah.infrastructure.config.build_ai_runtime_paths import resolve_active_ai_model_path


def parse_ai_command_draft_from_llm(
    command_text: str,
    runtime_paths: AiRuntimePaths,
    *,
    prefer_fallback_model: bool = False,
    return_raw_response: bool = False,
    dialogue_state: AiDialogueState | None = None,
    ui_context: AiUiContext | None = None,
    database_path: Path | None = None,
) -> AiCommandDraft | tuple[AiCommandDraft, str]:
    """Розбирає вільну команду через llama-server.
    Parses a free-form command through llama-server.
    """

    try:
        response_text = _request_llm_response(
            command_text,
            runtime_paths,
            prefer_fallback_model=prefer_fallback_model,
            dialogue_state=dialogue_state,
            ui_context=ui_context,
            database_path=database_path,
        )
    except LlamaServerHttpError as error:
        if not prefer_fallback_model:
            response_text = _request_llm_response(
                command_text,
                runtime_paths,
                prefer_fallback_model=True,
                dialogue_state=dialogue_state,
                ui_context=ui_context,
                database_path=database_path,
            )
        else:
            raise RuntimeError(
                f"llama-server HTTP {error.status_code} "
                f"(payload={error.request_bytes} B): {error.response_body[:300]}"
            ) from error

    payload = extract_json_object_from_llm_text(response_text)
    draft = _map_llm_payload_to_command_draft(command_text, payload)
    if return_raw_response:
        return draft, response_text
    return draft


def _request_llm_response(
    command_text: str,
    runtime_paths: AiRuntimePaths,
    *,
    prefer_fallback_model: bool,
    dialogue_state: AiDialogueState | None,
    ui_context: AiUiContext | None,
    database_path: Path | None = None,
) -> str:
    model_path = resolve_active_ai_model_path(runtime_paths, prefer_fallback=prefer_fallback_model)
    base_url = ensure_llama_server_running(runtime_paths, model_path)
    user_prompt = build_ai_llm_user_prompt(
        command_text,
        dialogue_state=dialogue_state,
        ui_context=ui_context,
        database_path=database_path,
    )
    system_prompt = build_ai_unified_system_prompt(command_text)
    return request_llama_chat_completion(
        base_url,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
    )


def _map_llm_payload_to_command_draft(command_text: str, payload: dict[str, object]) -> AiCommandDraft:
    if _looks_like_semantic_payload(payload):
        semantic_draft = map_ai_semantic_payload_to_draft(command_text, payload)
        adapted_draft = adapt_semantic_draft_to_command_draft(semantic_draft, source="llm")
        if adapted_draft is not None:
            return adapted_draft

        legacy_draft = map_ai_payload_to_draft(command_text, payload)
        if legacy_draft.intent != AiIntentKind.UNKNOWN:
            return legacy_draft

        return AiCommandDraft(
            intent=AiIntentKind.UNKNOWN,
            raw_command=command_text.strip(),
            source="semantic",
            clarification_message=(
                semantic_draft.clarification_message
                or "Команду розпізнано як семантичний намір, але цей тип дії ще не підключено до безпечного виконання."
            ),
        )

    return map_ai_payload_to_draft(command_text, payload)


def _looks_like_semantic_payload(payload: dict[str, object]) -> bool:
    return any(key in payload for key in ("mode", "module", "audience", "payload", "conditions"))
