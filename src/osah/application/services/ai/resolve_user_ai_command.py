from pathlib import Path

from dataclasses import replace

from osah.application.services.ai.build_ai_llm_user_prompt import build_ai_llm_user_prompt
from osah.application.services.ai.build_ai_unified_system_prompt import build_ai_unified_system_prompt
from osah.application.services.ai.ensure_ai_inspector_access import ensure_ai_inspector_access
from osah.application.services.ai.build_ai_operation_plan import build_ai_operation_plan
from osah.application.services.ai.ground_ai_command_draft import ground_ai_command_draft
from osah.application.services.ai.parse_ai_command_draft_from_llm import parse_ai_command_draft_from_llm
from osah.application.services.ai.serialize_ai_command_draft_for_trace import serialize_ai_command_draft_for_trace
from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_command_resolution import AiCommandResolution
from osah.domain.entities.ai_command_resolution_status import AiCommandResolutionStatus
from osah.domain.entities.ai_command_session import AiCommandSession
from osah.domain.entities.ai_conversation_context import AiConversationContext
from osah.domain.entities.ai_dialogue_state import AiDialogueState
from osah.domain.entities.ai_ui_context import AiUiContext
from osah.application.services.ai.prepare_ai_command_text_for_resolution import prepare_ai_command_text_for_resolution
from osah.application.services.ai.estimate_llm_prompt_tokens import estimate_llm_prompt_tokens, is_llm_prompt_over_budget
from osah.domain.services.ai.compiler.compile_ai_command import compile_ai_command, compile_command_text
from osah.domain.services.ai.compiler.fill_ai_command_session import fill_ai_command_session
from osah.domain.services.ai.convert_ai_dialogue_state import dialogue_state_from_conversation_context
from osah.domain.entities.ai_command_track import AiCommandTrack
from osah.domain.services.ai.classify_ai_resolution_track import classify_ai_resolution_track
from osah.domain.services.ai.detect_ai_command_track import detect_ai_command_track
from osah.domain.services.ai.try_build_draft_from_dialogue_state import try_build_draft_from_dialogue_state
from osah.domain.services.ai.try_match_department_combo_query import try_match_department_combo_query
from osah.domain.services.ai.try_match_department_employees_query import try_match_department_employees_query
from osah.domain.services.ai.try_match_high_confidence_fast_path_command import (
    try_match_high_confidence_fast_path_command,
)
from osah.domain.services.ai.try_match_intent_skeleton_command import try_match_intent_skeleton_command
from osah.domain.services.ai.validate_ai_command_draft import validate_ai_command_draft
from osah.domain.services.ai.build_bulk_audience_guided_choices import (
    build_bulk_audience_guided_choices,
    needs_bulk_audience_guided_clarify,
)
from osah.infrastructure.config.build_ai_runtime_paths import build_ai_runtime_paths, is_ai_runtime_bundle_available
from osah.infrastructure.logging.append_ai_command_trace import (
    append_ai_command_trace_step,
    begin_ai_command_trace,
    end_ai_command_trace,
)


def resolve_user_ai_command(
    command_text: str,
    *,
    access_role: AccessRole,
    project_root: Path | None = None,
    prefer_fallback_model: bool = False,
    database_path: Path | None = None,
    active_session: AiCommandSession | None = None,
    conversation_context: AiConversationContext | None = None,
    dialogue_state: AiDialogueState | None = None,
    ui_context: AiUiContext | None = None,
) -> AiCommandResolution:
    """Оркеструє rule-router, compiler, preflight і валідацію AI-команди.
    Orchestrates rule-router, compiler, preflight and AI command validation.
    """

    trace_id = begin_ai_command_trace(command_text)
    effective_dialogue_state = dialogue_state or dialogue_state_from_conversation_context(conversation_context)

    try:
        ensure_ai_inspector_access(access_role)
    except Exception as error:
        from osah.domain.errors.access_denied_error import AccessDeniedError

        if not isinstance(error, AccessDeniedError):
            raise
        resolution = AiCommandResolution(
            status=AiCommandResolutionStatus.ACCESS_DENIED,
            message=str(error),
            trace_id=trace_id,
        )
        _trace_resolution(trace_id, resolution)
        return resolution

    normalized_command = command_text.strip()
    if not normalized_command:
        resolution = AiCommandResolution(
            status=AiCommandResolutionStatus.NEEDS_CLARIFICATION,
            message="Введіть команду.",
            trace_id=trace_id,
        )
        _trace_resolution(trace_id, resolution)
        return resolution

    original_command, prepared_command = prepare_ai_command_text_for_resolution(
        normalized_command,
        database_path=database_path,
    )
    if prepared_command != normalized_command:
        append_ai_command_trace_step(
            trace_id,
            "PREPARE_TEXT",
            detail=f"prepared={prepared_command}",
        )

    if active_session is not None:
        append_ai_command_trace_step(trace_id, "SESSION_FILL", detail=normalized_command)
        compile_result = fill_ai_command_session(active_session, normalized_command)
        _trace_compile(trace_id, compile_result.draft, compile_result.missing_slots)
        return _finalize_compiled(
            compile_result,
            trace_id=trace_id,
            database_path=database_path,
            parent_trace_id=active_session.trace_id,
        )

    context_draft = try_build_draft_from_dialogue_state(
        prepared_command,
        effective_dialogue_state,
        database_path=database_path,
    )
    if context_draft is not None:
        append_ai_command_trace_step(
            trace_id,
            "DIALOGUE_STATE",
            detail="Follow-up збереженого стану діалогу.",
            payload=serialize_ai_command_draft_for_trace(context_draft),
        )
        compile_result = compile_ai_command(replace(context_draft, raw_command=original_command))
        _trace_compile(trace_id, compile_result.draft, compile_result.missing_slots)
        return _finalize_compiled(compile_result, trace_id=trace_id, database_path=database_path)

    combo_query_draft = try_match_department_combo_query(prepared_command)
    if combo_query_draft is not None:
        append_ai_command_trace_step(
            trace_id,
            "FAST_PATH",
            detail="Combo-запит підрозділ + проблеми інструктажів.",
            payload=serialize_ai_command_draft_for_trace(combo_query_draft),
        )
        compile_result = compile_ai_command(replace(combo_query_draft, raw_command=original_command))
        _trace_compile(trace_id, compile_result.draft, compile_result.missing_slots)
        return _finalize_compiled(compile_result, trace_id=trace_id, database_path=database_path)

    department_query_draft = try_match_department_employees_query(prepared_command)
    if department_query_draft is not None:
        append_ai_command_trace_step(
            trace_id,
            "FAST_PATH",
            detail="Запит списку працівників підрозділу.",
            payload=serialize_ai_command_draft_for_trace(department_query_draft),
        )
        compile_result = compile_ai_command(replace(department_query_draft, raw_command=original_command))
        _trace_compile(trace_id, compile_result.draft, compile_result.missing_slots)
        return _finalize_compiled(compile_result, trace_id=trace_id, database_path=database_path)

    fast_path_draft = try_match_high_confidence_fast_path_command(prepared_command)
    if fast_path_draft is not None:
        append_ai_command_trace_step(
            trace_id,
            "FAST_PATH",
            detail="Високовпевнений детермінований шлях.",
            payload=serialize_ai_command_draft_for_trace(fast_path_draft),
        )
        compile_result = compile_ai_command(replace(fast_path_draft, raw_command=original_command))
        _trace_compile(trace_id, compile_result.draft, compile_result.missing_slots)
        return _finalize_compiled(compile_result, trace_id=trace_id, database_path=database_path)

    resolution_track = classify_ai_resolution_track(prepared_command)

    runtime_paths = build_ai_runtime_paths(project_root)
    llm_attempted = False
    if is_ai_runtime_bundle_available(runtime_paths):
        llm_attempted = True
        append_ai_command_trace_step(trace_id, "LLM_PATH", detail="LLM-first розбір команди.")
        llm_resolution = _resolve_with_llm(
            original_command,
            prepared_command=prepared_command,
            runtime_paths=runtime_paths,
            prefer_fallback_model=prefer_fallback_model,
            database_path=database_path,
            trace_id=trace_id,
            dialogue_state=effective_dialogue_state,
            ui_context=ui_context,
        )
        if llm_resolution is not None:
            return llm_resolution
        if resolution_track == AiCommandTrack.WRITE:
            return _write_llm_unavailable_resolution(
                trace_id,
                runtime_missing=False,
            )

    if resolution_track == AiCommandTrack.WRITE:
        return _write_llm_unavailable_resolution(
            trace_id,
            runtime_missing=not llm_attempted,
        )

    skeleton_resolution = _resolve_with_intent_skeleton(
        prepared_command,
        original_command=original_command,
        trace_id=trace_id,
        database_path=database_path,
        runtime_unavailable=llm_attempted,
    )
    if skeleton_resolution is not None:
        return skeleton_resolution

    compiled = compile_command_text(
        prepared_command,
        raw_command=original_command,
        allow_write_fallback=False,
    )
    if compiled is not None and not compiled.needs_llm:
        append_ai_command_trace_step(
            trace_id,
            "COMPILE",
            detail="Fallback детермінований шлях без LLM.",
            payload=serialize_ai_command_draft_for_trace(compiled.draft),
        )
        return _finalize_compiled(compiled, trace_id=trace_id, database_path=database_path)

    resolution = AiCommandResolution(
        status=AiCommandResolutionStatus.RUNTIME_UNAVAILABLE,
        message="Локальний AI-runtime недоступний.",
        trace_id=trace_id,
    )
    _trace_resolution(trace_id, resolution)
    return resolution


def _write_llm_unavailable_resolution(
    trace_id: str,
    *,
    runtime_missing: bool,
) -> AiCommandResolution:
    """Повертає fail-closed для write/bulk без успішного LLM.
    Returns fail-closed resolution for write/bulk without successful LLM.
    """

    if runtime_missing:
        message = "Локальний AI-runtime недоступний. Write-команди потребують моделі."
    else:
        message = "Не вдалося розібрати команду без моделі. Спробуйте коротше або пізніше."
    resolution = AiCommandResolution(
        status=AiCommandResolutionStatus.LLM_UNAVAILABLE,
        message=message,
        trace_id=trace_id,
    )
    _trace_resolution(trace_id, resolution)
    return resolution


def _resolve_with_intent_skeleton(
    prepared_command: str,
    *,
    original_command: str,
    trace_id: str,
    database_path: Path | None,
    runtime_unavailable: bool,
) -> AiCommandResolution | None:
    skeleton_draft = try_match_intent_skeleton_command(prepared_command)
    if skeleton_draft is None:
        return None

    append_ai_command_trace_step(
        trace_id,
        "INTENT_SKELETON",
        detail="Детермінований розбір без LLM.",
        payload=serialize_ai_command_draft_for_trace(skeleton_draft),
    )
    compile_result = compile_ai_command(replace(skeleton_draft, raw_command=original_command))
    _trace_compile(trace_id, compile_result.draft, compile_result.missing_slots)
    resolution = _finalize_compiled(compile_result, trace_id=trace_id, database_path=database_path)
    if runtime_unavailable and resolution.status == AiCommandResolutionStatus.PARSED:
        resolution = AiCommandResolution(
            status=resolution.status,
            message="Локальна модель недоступна, відповів за правилами.",
            draft=resolution.draft,
            trace_id=resolution.trace_id,
        )
        _trace_resolution(trace_id, resolution)
    return resolution


def _resolve_with_llm(
    original_command: str,
    *,
    prepared_command: str,
    runtime_paths,
    prefer_fallback_model: bool,
    database_path: Path | None,
    trace_id: str,
    dialogue_state: AiDialogueState | None,
    ui_context: AiUiContext | None,
) -> AiCommandResolution | None:
    llm_command = prepared_command
    try:
        if prepared_command != original_command:
            append_ai_command_trace_step(
                trace_id,
                "PATTERN_MEMORY",
                detail=f"Текст для LLM: {llm_command}",
            )
        user_prompt = build_ai_llm_user_prompt(
            llm_command,
            dialogue_state=dialogue_state,
            ui_context=ui_context,
            database_path=database_path,
        )
        system_prompt = build_ai_unified_system_prompt(llm_command)
        estimated_tokens = estimate_llm_prompt_tokens(system_prompt, user_prompt)
        append_ai_command_trace_step(
            trace_id,
            "LLM_PAYLOAD_SIZE",
            detail=(
                f"system={len(system_prompt)}; user={len(user_prompt)}; "
                f"total={len(system_prompt) + len(user_prompt)}; est_tokens={estimated_tokens}"
            ),
        )
        if is_llm_prompt_over_budget(system_prompt, user_prompt):
            append_ai_command_trace_step(
                trace_id,
                "LLM_BUDGET_WARN",
                detail="Оцінка промпта перевищує практичний бюджет контексту.",
            )
        llm_draft, llm_raw_response = parse_ai_command_draft_from_llm(
            llm_command,
            runtime_paths,
            prefer_fallback_model=prefer_fallback_model,
            return_raw_response=True,
            dialogue_state=dialogue_state,
            ui_context=ui_context,
            database_path=database_path,
        )
        append_ai_command_trace_step(
            trace_id,
            "LLM_RAW",
            detail=llm_raw_response.strip() or "(порожня відповідь)",
        )
        append_ai_command_trace_step(
            trace_id,
            "LLM_DRAFT",
            payload=serialize_ai_command_draft_for_trace(llm_draft),
        )
        track = detect_ai_command_track(llm_draft)
        if track is not None:
            append_ai_command_trace_step(trace_id, "TRACK", detail=f"detected_track={track.value}")
    except (RuntimeError, TimeoutError, ValueError) as error:
        append_ai_command_trace_step(trace_id, "LLM_ERROR", detail=str(error))
        return None

    compile_result = compile_ai_command(replace(llm_draft, raw_command=original_command))
    _trace_compile(trace_id, compile_result.draft, compile_result.missing_slots)
    return _finalize_compiled(compile_result, trace_id=trace_id, database_path=database_path)


def _finalize_compiled(
    compile_result,
    *,
    trace_id: str,
    database_path: Path | None,
    parent_trace_id: str | None = None,
) -> AiCommandResolution:
    draft = compile_result.draft

    if draft.clarification_message:
        guided_choices = ()
        if needs_bulk_audience_guided_clarify(draft):
            guided_choices = build_bulk_audience_guided_choices()
        resolution = AiCommandResolution(
            status=AiCommandResolutionStatus.NEEDS_CLARIFICATION,
            message=draft.clarification_message,
            draft=draft,
            trace_id=trace_id or parent_trace_id,
            entity_choices=guided_choices,
            pending_grounding_choice_kind="bulk_audience_hint" if guided_choices else None,
        )
        _trace_resolution(trace_id, resolution)
        return resolution

    if compile_result.missing_slots:
        session = AiCommandSession(
            draft=draft,
            missing_slots=compile_result.missing_slots,
            prompt_message=compile_result.session_prompt or "Уточніть команду.",
            trace_id=trace_id or parent_trace_id,
        )
        resolution = AiCommandResolution(
            status=AiCommandResolutionStatus.NEEDS_CLARIFICATION,
            message=session.prompt_message,
            draft=draft,
            trace_id=trace_id or parent_trace_id,
            session=session,
        )
        append_ai_command_trace_step(
            trace_id,
            "SESSION",
            detail=f"missing={','.join(slot.value for slot in compile_result.missing_slots)}",
        )
        _trace_resolution(trace_id, resolution)
        return resolution

    if database_path is not None:
        grounding = ground_ai_command_draft(database_path, draft)
        append_ai_command_trace_step(
            trace_id,
            "GROUNDING",
            detail="OK" if grounding.ok else grounding.message,
            payload=serialize_ai_command_draft_for_trace(grounding.draft),
        )
        if not grounding.ok:
            resolution = AiCommandResolution(
                status=AiCommandResolutionStatus.NEEDS_CLARIFICATION,
                message=grounding.message,
                draft=draft,
                trace_id=trace_id or parent_trace_id,
                entity_choices=grounding.choices,
                pending_grounding_choice_kind=grounding.choice_kind,
            )
            _trace_resolution(trace_id, resolution)
            return resolution
        draft = grounding.draft

    operation_plan = build_ai_operation_plan(draft, database_path=database_path)
    append_ai_command_trace_step(
        trace_id,
        "PLAN",
        detail=(
            f"kind={operation_plan.kind.value}; mode={operation_plan.mode.value}; "
            f"confirm={operation_plan.requires_confirmation}; preview={operation_plan.requires_preview}; "
            f"can_execute={operation_plan.can_execute}"
        ),
        payload=serialize_ai_command_draft_for_trace(operation_plan.draft),
    )
    if not operation_plan.can_execute:
        resolution = AiCommandResolution(
            status=AiCommandResolutionStatus.NEEDS_CLARIFICATION,
            message="; ".join(operation_plan.issues),
            draft=operation_plan.draft,
            trace_id=trace_id or parent_trace_id,
        )
        _trace_resolution(trace_id, resolution)
        return resolution

    draft = operation_plan.draft
    issues = validate_ai_command_draft(draft)
    if issues:
        append_ai_command_trace_step(trace_id, "VALIDATE", detail="; ".join(issues))
        resolution = AiCommandResolution(
            status=AiCommandResolutionStatus.INVALID_DRAFT,
            message="; ".join(issues),
            draft=draft,
            trace_id=trace_id or parent_trace_id,
        )
        _trace_resolution(trace_id, resolution)
        return resolution

    append_ai_command_trace_step(trace_id, "VALIDATE", detail="OK")
    resolution = AiCommandResolution(
        status=AiCommandResolutionStatus.PARSED,
        message="Чернетку команди підготовлено.",
        draft=draft,
        trace_id=trace_id or parent_trace_id,
    )
    _trace_resolution(trace_id, resolution)
    return resolution


def _trace_compile(trace_id: str, draft: AiCommandDraft, missing_slots) -> None:
    detail = "OK"
    if missing_slots:
        detail = f"missing={','.join(slot.value for slot in missing_slots)}"
    append_ai_command_trace_step(
        trace_id,
        "COMPILE",
        detail=detail,
        payload=serialize_ai_command_draft_for_trace(draft),
    )


def _trace_resolution(trace_id: str, resolution: AiCommandResolution) -> None:
    append_ai_command_trace_step(
        trace_id,
        "RESOLUTION",
        detail=f"status={resolution.status.value}; message={resolution.message}",
        payload=serialize_ai_command_draft_for_trace(resolution.draft),
    )
    if resolution.status != AiCommandResolutionStatus.PARSED:
        end_ai_command_trace(trace_id, outcome=resolution.status.value)
