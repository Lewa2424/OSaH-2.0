"""Фази компіляції AI-команди.
AI command compiler phases.
"""

from __future__ import annotations

import re
from dataclasses import replace

from osah.domain.entities.ai_bulk_audience_spec import AiBulkAudienceSpec
from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.services.ai.compiler.ai_slot_extractors import (
    extract_bulk_slots,
    extract_list_query_slots,
    extract_write_slots,
)
from osah.domain.services.ai.ensure_ai_intent_is_allowed import (
    is_ai_answer_intent,
    is_ai_bulk_intent,
    is_ai_navigation_intent,
    is_ai_write_intent,
)
from osah.domain.services.ai.extract_bulk_audience_from_command import (
    extract_bulk_audience_from_command,
    has_implicit_bulk_audience_marker,
    is_department_audience_in_command,
)
from osah.domain.services.ai.extract_employee_query_from_command import extract_employee_query_from_command
from osah.domain.services.ai.has_bulk_audience_narrowing import has_bulk_audience_narrowing
from osah.domain.services.ai.matches_employee_problems_query import matches_employee_problems_query
from osah.domain.services.ai.merge_ai_bulk_audience_specs import merge_ai_bulk_audience_specs
from osah.domain.services.ai.reconcile_ai_command_track import reconcile_ai_command_track
from osah.domain.services.ai.reconcile_medical_extension_command import reconcile_medical_extension_command
from osah.domain.services.ai.reconcile_module_status_query import reconcile_module_status_query
from osah.domain.services.ai.reconcile_write_create_command import reconcile_write_create_command
from osah.domain.services.ai.demote_single_employee_bulk_draft import demote_single_employee_bulk_draft
from osah.domain.services.ai.reconcile_medical_restriction_command import reconcile_medical_restriction_command
from osah.domain.services.ai.should_preserve_trusted_semantic_slot import (
    should_block_bulk_intent_promotion,
    should_preserve_trusted_slot,
)

_VAGUE_BULK_APPLY_PATTERN = re.compile(
    r"^\s*(?:застосуй|зроби|примени)\s+(?:до\s+всіх|до\s+всех|пакетно)\s*$",
    re.IGNORECASE,
)
_BULK_PATTERN = re.compile(
    r"(?:\b(?:всім|усім|всем|групі|группе|групою|пакетно|масово|массово|"
    r"для\s+всіх|для\s+всех|вибраним|выбранным|списком|списку)\b)",
    re.IGNORECASE,
)
_EXPLAIN_PATTERN = re.compile(
    r"(?:поясн|поясни|пояснення|объясни|explain|що\s+таке|что\s+такое|"
    r"чому|почему|як\s+працює|как\s+работает|що\s+означає|что\s+означает)",
    re.IGNORECASE,
)
_OVERDUE_WORD_PATTERN = re.compile(r"(?:просроч|простроч|overdue)", re.IGNORECASE)
_CLOSE_TODAY_PATTERN = re.compile(
    r"(?:закрити|закрыть|закрит|закрыт).{0,30}(?:сьогодні|сегодня|today)",
    re.IGNORECASE,
)
_DELETE_COMMAND_PATTERN = re.compile(
    r"(?<!не\s)(?<!не)(?:\bвидали\b|\bудали\b|\bdelete\b)",
    re.IGNORECASE,
)

_POINT_TO_BULK_INTENT = {
    AiIntentKind.CREATE_TRAINING_RECORD: AiIntentKind.BULK_CREATE_TRAINING_RECORD,
    AiIntentKind.CREATE_PPE_ISSUANCE: AiIntentKind.BULK_CREATE_PPE_ISSUANCE,
    AiIntentKind.CREATE_MEDICAL_RECORD: AiIntentKind.BULK_CREATE_MEDICAL_RECORD,
    AiIntentKind.UPDATE_EMPLOYEE_FIELDS: AiIntentKind.BULK_UPDATE_EMPLOYEE_FIELDS,
    AiIntentKind.ADD_WORK_PERMIT_PARTICIPANT: AiIntentKind.BULK_ADD_WORK_PERMIT_PARTICIPANTS,
}


_LLM_TRUSTED_SOURCES = frozenset({"llm", "pattern_memory", "session", "dialogue_state"})


def _should_preserve_trusted_bulk_audience(draft: AiCommandDraft) -> bool:
    """Не перезаписує bulk-аудиторію regex-ом, якщо LLM уже дав звуження.
    Skips regex bulk-audience overwrite when a trusted source already narrowed it.
    """

    return should_preserve_trusted_slot(draft, "bulk_audience_spec")


def _allows_regex_write_promotion(draft: AiCommandDraft) -> bool:
    """Чи дозволено regex-промоцію write/bulk для цього джерела чернетки.
    Whether regex write/bulk promotion is allowed for this draft source.
    """

    return draft.source in _LLM_TRUSTED_SOURCES


def phase_align_intent(draft: AiCommandDraft) -> AiCommandDraft:
    """Вирівнює intent і маршрутизацію (колишній reconcile).
    Aligns intent routing (former reconcile pipeline).
    """

    raw_command = draft.raw_command.strip()
    if not raw_command:
        return draft

    draft = reconcile_module_status_query(draft)
    if draft.intent == AiIntentKind.QUERY_MODULE_STATUS:
        return draft

    if _allows_regex_write_promotion(draft):
        draft = reconcile_medical_restriction_command(draft)

    if _VAGUE_BULK_APPLY_PATTERN.search(raw_command) and _allows_regex_write_promotion(draft):
        return replace(
            draft,
            intent=AiIntentKind.BULK_CREATE_PPE_ISSUANCE,
            clarification_message="Уточніть дію та аудиторію: наприклад «Видай каски всім стропальникам дільниці N2».",
        )

    skip_bulk_promotion = (
        is_ai_answer_intent(draft.intent)
        or is_ai_navigation_intent(draft.intent)
        or should_block_bulk_intent_promotion(draft)
    )

    if _allows_regex_write_promotion(draft) and not skip_bulk_promotion and (
        _BULK_PATTERN.search(raw_command)
        or (is_ai_bulk_intent(draft.intent) and not should_block_bulk_intent_promotion(draft))
        or has_implicit_bulk_audience_marker(raw_command)
    ):
        return demote_single_employee_bulk_draft(_compile_bulk_draft(draft, raw_command))

    lowered = raw_command.lower()
    if any(token in lowered for token in ("створи працівника", "создай сотрудника", "додай працівника", "добавь сотрудника")):
        return replace(
            draft,
            intent=AiIntentKind.UNKNOWN,
            clarification_message="Створення нової картки працівника через AI поки не підтримується.",
        )

    if _DELETE_COMMAND_PATTERN.search(raw_command):
        return replace(
            draft,
            intent=AiIntentKind.UNKNOWN,
            clarification_message="Видалення записів через AI заборонено.",
        )

    if _allows_regex_write_promotion(draft):
        draft = reconcile_ai_command_track(draft)
        draft = reconcile_medical_extension_command(draft)
        draft = reconcile_write_create_command(draft)
        draft = demote_single_employee_bulk_draft(draft)

    if matches_employee_problems_query(raw_command):
        employee_query = (draft.employee_query or extract_employee_query_from_command(raw_command) or "").strip()
        if employee_query or draft.personnel_number:
            return replace(
                draft,
                intent=AiIntentKind.QUERY_EMPLOYEE_READINESS,
                employee_query=employee_query or None,
                module_key="all",
            )

    if draft.intent == AiIntentKind.QUERY_SECTION_PROBLEMS:
        employee_query = (draft.employee_query or extract_employee_query_from_command(raw_command) or "").strip()
        if employee_query or draft.personnel_number:
            return replace(
                draft,
                intent=AiIntentKind.QUERY_EMPLOYEE_READINESS,
                employee_query=employee_query or None,
                module_key="all",
            )

    if draft.intent == AiIntentKind.QUERY_MISSING_PPE and (draft.employee_query or draft.personnel_number):
        if not (draft.ppe_item_query or "").strip():
            return replace(
                draft,
                intent=AiIntentKind.QUERY_EMPLOYEE_READINESS,
            )

    if draft.intent == AiIntentKind.SHOW_OVERDUE and _CLOSE_TODAY_PATTERN.search(raw_command):
        if not _OVERDUE_WORD_PATTERN.search(raw_command):
            return replace(draft, intent=AiIntentKind.QUERY_DAILY_FOCUS)

    if draft.intent == AiIntentKind.GENERATE_REPORT_TEXT and _EXPLAIN_PATTERN.search(raw_command):
        module_key = draft.module_key or draft.section_key
        if not module_key and "інструктаж" in lowered:
            module_key = "trainings"
        elif not module_key and "мед" in lowered:
            module_key = "medical"
        elif not module_key and any(token in lowered for token in ("зіз", "сиз", "ppe")):
            module_key = "ppe"
        return replace(
            draft,
            intent=AiIntentKind.EXPLAIN_HELP,
            explain_topic="domain" if "що таке" in lowered or "что такое" in lowered else "status",
            module_key=module_key,
        )

    if draft.intent == AiIntentKind.UNKNOWN and _EXPLAIN_PATTERN.search(raw_command):
        return replace(
            draft,
            intent=AiIntentKind.EXPLAIN_HELP,
            explain_topic=_detect_explain_topic(raw_command),
        )

    if any(token in lowered for token in ("додай ризик", "добавь риск", "утверди port", "утверди port-r", "approve port")):
        return replace(
            draft,
            intent=AiIntentKind.UNKNOWN,
            clarification_message="Зміни PORT-R через AI поки не підтримуються.",
        )

    return draft


def phase_extract_slots(draft: AiCommandDraft) -> AiCommandDraft:
    """Доповнює чернетку слотами після вирівнювання intent.
    Enriches the draft with extracted slots after intent alignment.
    """

    if draft.intent == AiIntentKind.QUERY_MODULE_STATUS:
        return extract_list_query_slots(draft)
    if is_ai_bulk_intent(draft.intent):
        return extract_bulk_slots(draft)
    if is_ai_write_intent(draft.intent):
        return extract_write_slots(draft)
    return draft


def _compile_bulk_draft(draft: AiCommandDraft, raw_command: str) -> AiCommandDraft:
    promoted_intent = _promote_bulk_intent(draft, raw_command)
    audience_spec = _build_bulk_audience_spec(draft, raw_command)
    reconciled = replace(
        draft,
        intent=promoted_intent,
        bulk_audience_spec=audience_spec,
        employee_query=None if audience_spec and is_department_audience_in_command(raw_command, draft.employee_query) else draft.employee_query,
        needs_confirmation=True,
    )
    if audience_spec is None or not has_bulk_audience_narrowing(audience_spec):
        return replace(
            reconciled,
            clarification_message=(
                "Уточніть аудиторію: вкажіть ПІБ/таб.№, дільницю, посаду, наряд або інший критерій звуження."
            ),
        )
    return reconciled


def _promote_bulk_intent(draft: AiCommandDraft, raw_command: str) -> AiIntentKind:
    if is_ai_bulk_intent(draft.intent):
        return draft.intent
    if draft.intent in _POINT_TO_BULK_INTENT:
        return _POINT_TO_BULK_INTENT[draft.intent]
    return _infer_bulk_intent_from_text(raw_command)


def _infer_bulk_intent_from_text(raw_command: str) -> AiIntentKind:
    lowered = raw_command.lower()
    if any(token in lowered for token in ("інструктаж", "инструктаж")):
        return AiIntentKind.BULK_CREATE_TRAINING_RECORD
    if any(token in lowered for token in ("зіз", "сиз", "каск", "ppe", "спецодяг", "перчат", "рукавиц", "ботинк")):
        return AiIntentKind.BULK_CREATE_PPE_ISSUANCE
    if any(token in lowered for token in ("мед", "медогляд", "медосмотр")):
        return AiIntentKind.BULK_CREATE_MEDICAL_RECORD
    if any(token in lowered for token in ("посад", "дільниц", "участок", "підрозділ", "звільн")):
        return AiIntentKind.BULK_UPDATE_EMPLOYEE_FIELDS
    if any(token in lowered for token in ("наряд", "учасник", "бригад")):
        return AiIntentKind.BULK_ADD_WORK_PERMIT_PARTICIPANTS
    return AiIntentKind.UNKNOWN


def _build_bulk_audience_spec(draft: AiCommandDraft, raw_command: str) -> AiBulkAudienceSpec | None:
    if _should_preserve_trusted_bulk_audience(draft):
        return draft.bulk_audience_spec

    extracted = extract_bulk_audience_from_command(raw_command)
    from_draft = _build_bulk_audience_spec_from_draft(draft, raw_command)
    merged = merge_ai_bulk_audience_specs(extracted, draft.bulk_audience_spec)
    merged = merge_ai_bulk_audience_specs(merged, from_draft)

    if is_department_audience_in_command(raw_command, draft.employee_query):
        department_query = (draft.employee_query or "").strip()
        if department_query:
            if merged is None:
                merged = AiBulkAudienceSpec(department_query=department_query, combine_mode="and")
            else:
                merged = replace(merged, department_query=department_query)

    return merged


def _build_bulk_audience_spec_from_draft(draft: AiCommandDraft, raw_command: str) -> AiBulkAudienceSpec | None:
    employee_queries = _split_employee_queries(draft.employee_query)
    resolved_numbers: tuple[str, ...] = ()
    if draft.bulk_audience_spec is not None and draft.bulk_audience_spec.resolved_personnel_numbers:
        resolved_numbers = draft.bulk_audience_spec.resolved_personnel_numbers
    elif draft.personnel_number:
        resolved_numbers = (draft.personnel_number,)
    elif draft.resolved_audience:
        resolved_numbers = draft.resolved_audience

    filter_key = draft.filter_key
    lowered = raw_command.lower()
    if not filter_key and any(token in lowered for token in ("активн", "активные")):
        filter_key = "active"
    if any(token in lowered for token in ("стропальник", "стропальщик")):
        filter_key = filter_key or "slinger"

    department_query = None
    position_query = None
    extracted = extract_bulk_audience_from_command(raw_command)
    if extracted is not None:
        department_query = extracted.department_query
        position_query = extracted.position_query

    permit_number = draft.permit_number
    if extracted is not None and extracted.permit_number:
        permit_number = permit_number or extracted.permit_number
    if not permit_number:
        permit_match = re.search(r"(?:наряд[уа]?|№)\s*(\d+)", raw_command, re.IGNORECASE)
        if permit_match:
            permit_number = permit_match.group(1)

    if not any((employee_queries, resolved_numbers, filter_key, department_query, permit_number)):
        return None

    return AiBulkAudienceSpec(
        employee_queries=employee_queries,
        resolved_personnel_numbers=resolved_numbers,
        department_query=department_query,
        position_query=position_query,
        filter_key=filter_key,
        permit_number=permit_number,
        combine_mode="and",
    )


def _split_employee_queries(employee_query: str | None) -> tuple[str, ...]:
    if not employee_query:
        return ()
    normalized = employee_query.replace(" та ", ",").replace(" і ", ",").replace(" и ", ",")
    parts = [part.strip() for part in normalized.split(",") if part.strip()]
    if len(parts) <= 1:
        return ()
    return tuple(parts)


def _detect_explain_topic(raw_command: str) -> str:
    lowered = raw_command.lower()
    if any(token in lowered for token in ("помилк", "ошибк", "не знайден", "не найден", "не можна зберегти")):
        return "error"
    if any(token in lowered for token in ("поле", "кнопк", "екран", "розділ", "раздел", "read-only")):
        return "ui"
    if any(token in lowered for token in ("що таке", "что такое", "цільовий", "целевой", "наряд-допуск")):
        return "domain"
    if any(token in lowered for token in ("статус", "червон", "жовт", "чому", "почему")):
        return "status"
    if any(token in lowered for token in ("наряд", "port-r", "port r", "паспорт")):
        return "domain"
    return "domain"
