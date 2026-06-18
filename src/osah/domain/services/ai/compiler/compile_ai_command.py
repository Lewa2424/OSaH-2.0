from dataclasses import replace

from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_compile_result import AiCompileResult
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.services.ai.command_verb_tokens import sanitize_employee_query
from osah.domain.services.ai.compiler.ai_command_compile_phases import phase_align_intent, phase_extract_slots
from osah.domain.services.ai.compiler.ai_intent_slot_specs import list_missing_slots, session_prompt_for_slot
from osah.domain.services.ai.compiler.ai_slot_extractors import build_deterministic_draft_from_command
from osah.domain.entities.ai_command_track import AiCommandTrack
from osah.application.services.ai.build_ai_unified_system_prompt import is_write_command_text
from osah.domain.services.ai.detect_ai_command_track import detect_ai_command_track
from osah.domain.services.ai.ensure_ai_intent_is_allowed import is_ai_bulk_intent, is_ai_write_intent
from osah.domain.services.ai.should_preserve_trusted_semantic_slot import should_preserve_trusted_slot
from osah.domain.services.ai.extract_employee_query_from_command import extract_employee_query_from_command
from osah.domain.services.ai.normalize_ai_command_text import normalize_ai_command_text
from osah.domain.services.ai.semantic.adapt_semantic_draft_to_command_draft import (
    adapt_semantic_draft_to_command_draft,
)
from osah.domain.services.ai.semantic.build_ai_semantic_draft_from_command import build_ai_semantic_draft_from_command
from osah.domain.services.ai.try_match_simple_ai_command import try_match_simple_ai_command


def compile_ai_command(draft: AiCommandDraft) -> AiCompileResult:
    """Компілює чернетку: track → classify → extract → missing slots.
    Compiles a draft: track → classify → extract → missing slots.
    """

    if not draft.raw_command.strip():
        return AiCompileResult(draft=draft)

    semantic_draft = _build_command_draft_from_semantic(draft.raw_command, source=draft.source)
    if (
        semantic_draft is not None
        and draft.source in {"llm", "pattern_memory"}
        and _should_apply_semantic_override(draft, semantic_draft)
    ):
        return compile_ai_command(semantic_draft)

    aligned = phase_align_intent(draft)
    enriched = phase_extract_slots(aligned)
    enriched = _sanitize_draft_employee_query(enriched)
    missing_slots = list_missing_slots(enriched)
    session_prompt = session_prompt_for_slot(missing_slots[0]) if missing_slots else None
    needs_llm = enriched.intent == AiIntentKind.UNKNOWN and draft.source in {"llm", "pattern_memory"}

    return AiCompileResult(
        draft=enriched,
        missing_slots=missing_slots,
        needs_llm=needs_llm,
        session_prompt=session_prompt,
    )


def compile_command_text(
    command_text: str,
    *,
    source: str = "compiler",
    raw_command: str | None = None,
    allow_write_fallback: bool = True,
) -> AiCompileResult | None:
    """Компілює команду без LLM через rule-router або детермінований extract.
    Compiles a command without LLM via rule router or deterministic extract.
    """

    normalized = normalize_ai_command_text(command_text)
    original = (raw_command or command_text).strip()
    if not normalized and not original:
        return None

    routed = try_match_simple_ai_command(normalized)
    if routed is not None:
        return compile_ai_command(replace(routed, raw_command=original))

    list_result = _compile_list_query_without_llm(normalized, source=source, raw_command=original)
    if list_result is not None:
        return list_result

    if allow_write_fallback:
        semantic_draft = _build_command_draft_from_semantic(normalized, source=source)
        if semantic_draft is not None:
            return compile_ai_command(replace(semantic_draft, raw_command=original))

        deterministic = build_deterministic_draft_from_command(normalized)
        if deterministic is not None:
            deterministic = AiCommandDraft(
                intent=deterministic.intent,
                raw_command=original,
                source=source,
                employee_query=deterministic.employee_query,
                personnel_number=deterministic.personnel_number,
                items=deterministic.items,
                issue_date=deterministic.issue_date,
                ppe_item_query=deterministic.ppe_item_query,
                training_type=deterministic.training_type,
                module_key=deterministic.module_key,
                filter_key=deterministic.filter_key,
                next_control_date=deterministic.next_control_date,
                use_manual_next_control_date=deterministic.use_manual_next_control_date,
                work_risk_category=deterministic.work_risk_category,
                needs_confirmation=deterministic.needs_confirmation,
                bulk_audience_spec=deterministic.bulk_audience_spec,
            )
            return compile_ai_command(deterministic)

    probe = AiCommandDraft(intent=AiIntentKind.UNKNOWN, raw_command=original, source=source)
    if is_write_command_text(original) or is_write_command_text(normalized):
        return AiCompileResult(draft=probe, needs_llm=True)

    track = detect_ai_command_track(probe)
    if track is None or track == AiCommandTrack.WRITE:
        return AiCompileResult(draft=probe, needs_llm=True)

    return compile_ai_command(probe)


def _compile_list_query_without_llm(command_text: str, *, source: str, raw_command: str) -> AiCompileResult | None:
    from osah.domain.services.ai.extract_module_status_query_from_command import (
        extract_module_status_query_from_command,
    )

    extracted = extract_module_status_query_from_command(command_text)
    if extracted is None:
        return None
    module_key, filter_key = extracted
    draft = AiCommandDraft(
        intent=AiIntentKind.QUERY_MODULE_STATUS,
        raw_command=raw_command,
        source=source,
        module_key=module_key,
        filter_key=filter_key,
    )
    return compile_ai_command(draft)


def _build_command_draft_from_semantic(command_text: str, *, source: str) -> AiCommandDraft | None:
    semantic_draft = build_ai_semantic_draft_from_command(command_text)
    if semantic_draft is None:
        return None
    return adapt_semantic_draft_to_command_draft(semantic_draft, source=source)


def _should_apply_semantic_override(current_draft: AiCommandDraft, semantic_draft: AiCommandDraft) -> bool:
    if current_draft.intent == AiIntentKind.UNKNOWN:
        return True
    if is_ai_bulk_intent(semantic_draft.intent) and not is_ai_bulk_intent(current_draft.intent):
        if should_preserve_trusted_slot(current_draft, "intent"):
            return False
        if should_preserve_trusted_slot(current_draft, "employee_query") or should_preserve_trusted_slot(
            current_draft, "personnel_number"
        ):
            return False
        return True
    return False


def _sanitize_draft_employee_query(draft: AiCommandDraft) -> AiCommandDraft:
    if is_ai_bulk_intent(draft.intent):
        audience_spec = draft.bulk_audience_spec
        if audience_spec is not None and audience_spec.resolved_personnel_numbers:
            if draft.employee_query:
                return replace(draft, employee_query=None)
            return draft

    if should_preserve_trusted_slot(draft, "employee_query"):
        cleaned = sanitize_employee_query(draft.employee_query)
        if cleaned and _employee_query_needs_reextract(cleaned, draft.raw_command):
            cleaned = sanitize_employee_query(extract_employee_query_from_command(draft.raw_command))
        if cleaned != draft.employee_query:
            return replace(draft, employee_query=cleaned)
        return draft

    cleaned = sanitize_employee_query(draft.employee_query)
    if not cleaned:
        cleaned = sanitize_employee_query(extract_employee_query_from_command(draft.raw_command))
    if cleaned == draft.employee_query:
        return draft
    return replace(draft, employee_query=cleaned)


def _employee_query_needs_reextract(employee_query: str, raw_command: str) -> bool:
    lowered_query = employee_query.lower()
    lowered_command = raw_command.lower()
    if "ограничен" in lowered_query or "обмежен" in lowered_query:
        return True
    if len(employee_query.split()) > 4 and (
        "ограничен" in lowered_command or "обмежен" in lowered_command
    ):
        return True
    return False
