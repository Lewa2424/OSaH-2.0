import re

from osah.domain.entities.ai_bulk_audience_spec import AiBulkAudienceSpec
from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_employee_field_updates import AiEmployeeFieldUpdates
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.entities.ai_semantic_audience_type import AiSemanticAudienceType
from osah.domain.entities.ai_semantic_draft import AiSemanticDraft
from osah.domain.entities.ai_semantic_intent import AiSemanticIntent
from osah.domain.services.ai.normalize_ai_issue_date_text import normalize_ai_issue_date_text
from osah.domain.services.ai.semantic.collect_semantic_employee_queries import collect_semantic_employee_queries


def adapt_semantic_draft_to_command_draft(
    semantic_draft: AiSemanticDraft,
    *,
    source: str = "semantic",
) -> AiCommandDraft | None:
    """Адаптує semantic draft до поточного AiCommandDraft, якщо дію вже підтримано.
    Adapts a semantic draft to the current AiCommandDraft when supported.
    """

    intent = semantic_draft.intent
    if intent == AiSemanticIntent.CREATE_PPE_ISSUANCE:
        if semantic_draft.audience.audience_type in {
            AiSemanticAudienceType.DEPARTMENT,
            AiSemanticAudienceType.EMPLOYEE_LIST,
            AiSemanticAudienceType.EMPLOYEE_FILTER,
        }:
            return _bulk_draft(semantic_draft, AiIntentKind.BULK_CREATE_PPE_ISSUANCE, source=source)
        return _single_employee_draft(semantic_draft, AiIntentKind.CREATE_PPE_ISSUANCE, source=source)
    if intent == AiSemanticIntent.CREATE_PPE_ISSUANCE_FOR_WORK_PERMIT_PARTICIPANTS:
        return _bulk_draft(semantic_draft, AiIntentKind.BULK_CREATE_PPE_ISSUANCE, source=source)
    if intent == AiSemanticIntent.CREATE_TRAINING_RECORD:
        return _single_employee_draft(semantic_draft, AiIntentKind.CREATE_TRAINING_RECORD, source=source)
    if intent in {
        AiSemanticIntent.CREATE_TRAINING_BATCH,
        AiSemanticIntent.CREATE_TARGET_TRAINING_FOR_WORK_PERMIT,
    }:
        return _bulk_draft(semantic_draft, AiIntentKind.BULK_CREATE_TRAINING_RECORD, source=source)
    if intent == AiSemanticIntent.CREATE_OR_UPDATE_MEDICAL_RECORD:
        return _single_employee_draft(semantic_draft, AiIntentKind.CREATE_MEDICAL_RECORD, source=source)
    if intent == AiSemanticIntent.UPDATE_MEDICAL_BATCH:
        return _bulk_draft(semantic_draft, AiIntentKind.BULK_CREATE_MEDICAL_RECORD, source=source)
    if intent == AiSemanticIntent.UPDATE_EMPLOYEE_SITE_BATCH:
        return _bulk_employee_update_draft(semantic_draft, source=source)
    if intent == AiSemanticIntent.CREATE_WORK_PERMIT_DRAFT:
        return _create_work_permit_draft(semantic_draft, source=source)
    if intent == AiSemanticIntent.UPDATE_WORK_PERMIT_PARTICIPANTS:
        return _update_work_permit_participants_draft(semantic_draft, source=source)
    if intent == AiSemanticIntent.ADD_WORK_PERMIT_SAFETY_MEASURES:
        return _add_work_permit_safety_measures_draft(semantic_draft, source=source)
    if intent == AiSemanticIntent.PREPARE_EMPLOYEE_DATA_CLEANUP:
        return _employee_cleanup_query_draft(semantic_draft, source=source)
    if intent == AiSemanticIntent.REPLACE_PPE_ITEM:
        return _update_ppe_record_draft(semantic_draft, source=source)
    if intent == AiSemanticIntent.UPDATE_MEDICAL_RESTRICTION:
        return _update_medical_record_draft(semantic_draft, source=source)
    return None


def _semantic_conditions(semantic_draft: AiSemanticDraft) -> tuple[str, ...]:
    return tuple(condition.condition_type.value for condition in semantic_draft.conditions)


_SYMBOLIC_EVENT_DATES = frozenset({"сьогодні", "сегодня", "today", "завтра", "tomorrow"})


def _normalized_event_date(raw_value: str | None) -> str | None:
    if not raw_value or not raw_value.strip():
        return None
    stripped = raw_value.strip()
    if stripped.lower() in _SYMBOLIC_EVENT_DATES:
        return stripped
    if re.fullmatch(r"\d{1,2}\.\d{1,2}\.\d{4}", stripped):
        return stripped
    return normalize_ai_issue_date_text(stripped)


def _single_employee_draft(semantic_draft: AiSemanticDraft, intent: AiIntentKind, *, source: str) -> AiCommandDraft:
    payload = semantic_draft.payload
    employee_query = _first_employee_query(semantic_draft)
    return AiCommandDraft(
        intent=intent,
        raw_command=semantic_draft.raw_command,
        source=source,
        employee_query=employee_query,
        items=payload.items,
        issue_date=_normalized_event_date(payload.event_date),
        ppe_item_query=payload.ppe_item_query,
        training_type=payload.training_type,
        conducted_by=payload.conducted_by,
        valid_until_date=_normalized_event_date(payload.valid_until_date),
        restriction_note=payload.restriction_note,
        needs_confirmation=semantic_draft.needs_confirmation,
        semantic_conditions=_semantic_conditions(semantic_draft),
    )


def _bulk_draft(semantic_draft: AiSemanticDraft, intent: AiIntentKind, *, source: str) -> AiCommandDraft:
    payload = semantic_draft.payload
    audience = semantic_draft.audience
    return AiCommandDraft(
        intent=intent,
        raw_command=semantic_draft.raw_command,
        source=source,
        items=payload.items,
        issue_date=_normalized_event_date(payload.event_date),
        ppe_item_query=payload.ppe_item_query,
        training_type=payload.training_type,
        conducted_by=payload.conducted_by,
        valid_until_date=_normalized_event_date(payload.valid_until_date),
        restriction_note=payload.restriction_note,
        bulk_audience_spec=AiBulkAudienceSpec(
            employee_queries=audience.employee_queries,
            department_query=audience.department_query,
            position_query=audience.position_query,
            permit_number=audience.permit_number,
            filter_key=_first_filter(audience.filters),
            combine_mode="and",
        ),
        permit_number=audience.permit_number,
        needs_confirmation=semantic_draft.needs_confirmation,
        semantic_conditions=_semantic_conditions(semantic_draft),
    )


def _bulk_employee_update_draft(semantic_draft: AiSemanticDraft, *, source: str) -> AiCommandDraft:
    audience = semantic_draft.audience
    payload = semantic_draft.payload
    department_name = payload.department_name
    bulk_spec = AiBulkAudienceSpec(
        employee_queries=audience.employee_queries,
        department_query=audience.department_query or department_name,
        position_query=audience.position_query,
        filter_key=_first_filter(audience.filters),
        combine_mode="and",
    )
    return AiCommandDraft(
        intent=AiIntentKind.BULK_UPDATE_EMPLOYEE_FIELDS,
        raw_command=semantic_draft.raw_command,
        source=source,
        bulk_audience_spec=bulk_spec,
        employee_field_updates=AiEmployeeFieldUpdates(
            department_name=department_name,
            position_name=payload.position_name,
        ),
        issue_date=payload.effective_date,
        needs_confirmation=semantic_draft.needs_confirmation,
    )


def _create_work_permit_draft(semantic_draft: AiSemanticDraft, *, source: str) -> AiCommandDraft:
    payload = semantic_draft.payload
    audience = semantic_draft.audience
    permit_identifier = (audience.permit_number or "").strip()
    participant_queries = audience.employee_queries
    bulk_spec = None
    if participant_queries:
        bulk_spec = AiBulkAudienceSpec(
            employee_queries=participant_queries,
            resolved_personnel_numbers=tuple(
                query.strip()
                for query in participant_queries
                if query.strip().isdigit()
            ),
        )
    return AiCommandDraft(
        intent=AiIntentKind.CREATE_WORK_PERMIT_DRAFT,
        raw_command=semantic_draft.raw_command,
        source=source,
        permit_number=permit_identifier if permit_identifier.isdigit() else None,
        permit_query=permit_identifier or None,
        work_kind=payload.work_kind or "Наряд-допуск",
        work_location=payload.work_location or "Місце робіт",
        starts_at_text=payload.starts_at_text or "сьогодні 08:00",
        ends_at_text=payload.ends_at_text or "сьогодні 17:00",
        bulk_audience_spec=bulk_spec,
        needs_confirmation=semantic_draft.needs_confirmation,
    )


def _first_employee_query(semantic_draft: AiSemanticDraft) -> str | None:
    collected = collect_semantic_employee_queries(semantic_draft)
    return collected[0] if collected else None


def _first_filter(filters: tuple[str, ...]) -> str | None:
    return filters[0] if filters else None


def _employee_cleanup_query_draft(semantic_draft: AiSemanticDraft, *, source: str) -> AiCommandDraft:
    filters = semantic_draft.audience.filters
    filter_key = "without_department"
    if filters and "missing_position" in filters:
        filter_key = "without_position"
    if filters and "missing_department" in filters and "missing_position" in filters:
        filter_key = "without_department"
    return AiCommandDraft(
        intent=AiIntentKind.QUERY_EMPLOYEES_FILTER,
        raw_command=semantic_draft.raw_command,
        source=source,
        filter_key=filter_key,
        needs_confirmation=False,
    )


def _update_work_permit_participants_draft(semantic_draft: AiSemanticDraft, *, source: str) -> AiCommandDraft | None:
    payload = semantic_draft.payload
    audience = semantic_draft.audience
    add_queries = payload.add_employee_queries
    remove_queries = payload.remove_employee_queries
    if not add_queries and not remove_queries:
        return None
    bulk_spec = None
    if add_queries:
        bulk_spec = AiBulkAudienceSpec(
            employee_queries=add_queries,
            combine_mode="and",
        )
    if len(add_queries) == 1 and not remove_queries:
        return AiCommandDraft(
            intent=AiIntentKind.ADD_WORK_PERMIT_PARTICIPANT,
            raw_command=semantic_draft.raw_command,
            source=source,
            permit_number=audience.permit_number,
            employee_query=add_queries[0],
            needs_confirmation=semantic_draft.needs_confirmation,
        )
    if len(remove_queries) == 1 and not add_queries:
        return AiCommandDraft(
            intent=AiIntentKind.REMOVE_WORK_PERMIT_PARTICIPANT,
            raw_command=semantic_draft.raw_command,
            source=source,
            permit_number=audience.permit_number,
            employee_query=remove_queries[0],
            needs_confirmation=semantic_draft.needs_confirmation,
        )
    return AiCommandDraft(
        intent=AiIntentKind.BULK_ADD_WORK_PERMIT_PARTICIPANTS,
        raw_command=semantic_draft.raw_command,
        source=source,
        permit_number=audience.permit_number,
        bulk_audience_spec=bulk_spec,
        work_permit_remove_queries=remove_queries,
        needs_confirmation=semantic_draft.needs_confirmation,
    )


def _add_work_permit_safety_measures_draft(semantic_draft: AiSemanticDraft, *, source: str) -> AiCommandDraft:
    payload = semantic_draft.payload
    measures = payload.safety_measures
    note_text = "; ".join(measure.strip() for measure in measures if measure.strip())
    return AiCommandDraft(
        intent=AiIntentKind.CREATE_WORK_PERMIT_DRAFT,
        raw_command=semantic_draft.raw_command,
        source=source,
        work_kind=payload.work_kind or "Наряд-допуск",
        work_location=payload.work_location or "Місце робіт",
        starts_at_text=payload.starts_at_text or "сьогодні 08:00",
        ends_at_text=payload.ends_at_text or "сьогодні 17:00",
        restriction_note=note_text or None,
        needs_confirmation=semantic_draft.needs_confirmation,
    )


def _update_ppe_record_draft(semantic_draft: AiSemanticDraft, *, source: str) -> AiCommandDraft:
    payload = semantic_draft.payload
    return AiCommandDraft(
        intent=AiIntentKind.UPDATE_PPE_RECORD,
        raw_command=semantic_draft.raw_command,
        source=source,
        employee_query=_first_employee_query(semantic_draft),
        items=payload.items,
        ppe_item_query=payload.ppe_item_query,
        issue_date=payload.event_date,
        replacement_date=payload.event_date,
        needs_confirmation=semantic_draft.needs_confirmation,
    )


def _update_medical_record_draft(semantic_draft: AiSemanticDraft, *, source: str) -> AiCommandDraft:
    payload = semantic_draft.payload
    return AiCommandDraft(
        intent=AiIntentKind.UPDATE_MEDICAL_RECORD,
        raw_command=semantic_draft.raw_command,
        source=source,
        employee_query=_first_employee_query(semantic_draft),
        valid_until_date=payload.valid_until_date,
        restriction_note=payload.restriction_note,
        issue_date=payload.event_date,
        needs_confirmation=semantic_draft.needs_confirmation,
    )
