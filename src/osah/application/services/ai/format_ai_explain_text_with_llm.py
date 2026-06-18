from pathlib import Path

from osah.application.services.ai.build_ai_explain_grounding_facts import build_ai_explain_grounding_facts
from osah.domain.entities.ai_runtime_paths import AiRuntimePaths
from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_ui_context import AiUiContext
from osah.infrastructure.ai.llama_server_session import ensure_llama_server_running
from osah.infrastructure.ai.request_llama_chat_completion import request_llama_chat_completion
from osah.infrastructure.config.build_ai_runtime_paths import resolve_active_ai_model_path


def format_ai_explain_text_with_llm(
    database_path: Path,
    draft: AiCommandDraft,
    grounded_facts: str,
    runtime_paths: AiRuntimePaths,
    *,
    ui_context: AiUiContext | None = None,
    prefer_fallback_model: bool = False,
) -> str | None:
    """Формулює explain-відповідь через LLM лише на основі фактів з БД.
    Formats an explain answer via LLM using only database-grounded facts.
    """

    if not grounded_facts.strip():
        return None

    model_path = resolve_active_ai_model_path(runtime_paths, prefer_fallback=prefer_fallback_model)
    base_url = ensure_llama_server_running(runtime_paths, model_path)
    system_prompt = (
        "Ти помічник ClearWork AI. Сформулируй короткое понятное объяснение на русском или украинском "
        "только на основе переданных фактов. Не выдумывай данные. Если фактов мало — скажи, чего не хватает."
    )
    user_prompt = (
        f"Вопрос пользователя: {draft.raw_command.strip()}\n\n"
        f"Факты из системы:\n{grounded_facts.strip()}\n\n"
        "Дай ответ 2-5 предложениями."
    )
    response_text = request_llama_chat_completion(
        base_url,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
    )
    cleaned = response_text.strip()
    return cleaned or None
