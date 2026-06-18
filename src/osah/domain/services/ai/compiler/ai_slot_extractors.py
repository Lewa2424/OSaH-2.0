from dataclasses import replace

from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.entities.ai_item_draft import AiItemDraft
from osah.domain.services.ai.has_bulk_audience_narrowing import has_bulk_audience_narrowing
from osah.domain.services.ai.should_preserve_trusted_semantic_slot import should_preserve_trusted_slot
from osah.domain.services.ai.merge_ai_bulk_audience_specs import merge_ai_bulk_audience_specs
from osah.domain.services.ai.compiler.ai_slot_normalizers import (
    extract_work_risk_category_from_command,
    parse_relative_period_from_command,
)
from osah.domain.services.ai.detect_ai_command_track import (
    extract_ppe_token_from_command,
    has_today_date_marker,
    infer_write_module_key,
)
from osah.domain.services.ai.extract_bulk_audience_from_command import extract_bulk_audience_from_command
from osah.domain.services.ai.extract_employee_query_from_command import (
    extract_employee_query_from_command,
    extract_personnel_number_from_command,
)
from osah.domain.services.ai.extract_module_status_query_from_command import extract_module_status_query_from_command
from osah.domain.services.ai.normalize_ai_training_type import infer_ai_training_type_from_command


def extract_write_slots(draft: AiCommandDraft) -> AiCommandDraft:
    """Доповнює write-чернетку слотами з тексту команди.
    Enriches a write draft with slots extracted from command text.
    """

    raw_command = draft.raw_command.strip()
    if not raw_command:
        return draft

    employee_query_source = draft.employee_query
    if should_preserve_trusted_slot(draft, "employee_query"):
        employee_query = employee_query_source
    else:
        employee_query = employee_query_source or extract_employee_query_from_command(raw_command)
    if should_preserve_trusted_slot(draft, "personnel_number"):
        personnel_number = draft.personnel_number
    else:
        personnel_number = draft.personnel_number or extract_personnel_number_from_command(raw_command)
    employee_query, personnel_number = _resolve_employee_reference(employee_query, personnel_number)
    if should_preserve_trusted_slot(draft, "issue_date"):
        issue_date = draft.issue_date
    else:
        issue_date = draft.issue_date or ("сьогодні" if has_today_date_marker(raw_command) else None)
    next_control_date, use_manual = parse_relative_period_from_command(raw_command)
    if should_preserve_trusted_slot(draft, "work_risk_category"):
        work_risk = draft.work_risk_category
    else:
        work_risk = draft.work_risk_category or extract_work_risk_category_from_command(raw_command)

    updates: dict[str, object] = {}
    if employee_query and not personnel_number:
        updates["employee_query"] = employee_query
    if personnel_number:
        updates["personnel_number"] = personnel_number
        updates["employee_query"] = None
    if issue_date:
        updates["issue_date"] = issue_date
    if next_control_date:
        updates["next_control_date"] = next_control_date
        updates["use_manual_next_control_date"] = use_manual
    if work_risk:
        updates["work_risk_category"] = work_risk

    module_key = infer_write_module_key(raw_command, draft)
    if module_key == "ppe":
        if should_preserve_trusted_slot(draft, "ppe_item_query"):
            ppe_token = draft.ppe_item_query
        else:
            ppe_token = draft.ppe_item_query or extract_ppe_token_from_command(raw_command)
        if ppe_token and not should_preserve_trusted_slot(draft, "ppe_item_query"):
            updates["ppe_item_query"] = ppe_token
        if not draft.items and ppe_token and not should_preserve_trusted_slot(draft, "items"):
            updates["items"] = (AiItemDraft(name=ppe_token, quantity=1),)

    if module_key == "trainings":
        if should_preserve_trusted_slot(draft, "training_type"):
            training_type = draft.training_type
        else:
            training_type = infer_ai_training_type_from_command(raw_command) or draft.training_type
        if training_type:
            updates["training_type"] = training_type

    if not updates:
        return draft
    return replace(draft, **updates)


def extract_list_query_slots(draft: AiCommandDraft) -> AiCommandDraft:
    """Доповнює list-query чернетку module_key і filter_key.
    Enriches a list-query draft with module and status filters.
    """

    extracted = extract_module_status_query_from_command(draft.raw_command)
    if extracted is None:
        return draft
    module_key, filter_key = extracted
    return replace(draft, module_key=module_key, filter_key=filter_key, employee_query=None, personnel_number=None)


def extract_bulk_slots(draft: AiCommandDraft) -> AiCommandDraft:
    """Доповнює bulk-чернетку аудиторією та слотами видачі з тексту.
    Enriches a bulk draft with audience and issuance slots extracted from text.
    """

    raw_command = draft.raw_command.strip()
    updates: dict[str, object] = {}

    preserve_audience = should_preserve_trusted_slot(draft, "bulk_audience_spec")
    if not preserve_audience:
        extracted_spec = extract_bulk_audience_from_command(raw_command)
        if extracted_spec is not None:
            merged_spec = merge_ai_bulk_audience_specs(draft.bulk_audience_spec, extracted_spec)
            if merged_spec is not None:
                updates["bulk_audience_spec"] = merged_spec

    if draft.intent == AiIntentKind.BULK_CREATE_PPE_ISSUANCE:
        ppe_token = draft.ppe_item_query or extract_ppe_token_from_command(raw_command)
        if ppe_token:
            updates["ppe_item_query"] = ppe_token
        if not draft.items and ppe_token:
            updates["items"] = (AiItemDraft(name=ppe_token, quantity=1),)
        if not draft.issue_date and has_today_date_marker(raw_command):
            updates["issue_date"] = "сьогодні"

    if not updates:
        return draft
    return replace(draft, **updates)


def build_deterministic_draft_from_command(command_text: str) -> AiCommandDraft | None:
    """Будує початкову чернетку без LLM для write/list-команд.
    Builds an initial draft without LLM for write or list commands.
    """

    raw_command = command_text.strip()
    if not raw_command:
        return None

    list_extracted = extract_module_status_query_from_command(raw_command)
    if list_extracted is not None:
        return None

    module_key = infer_write_module_key(raw_command, AiCommandDraft(intent=AiIntentKind.UNKNOWN, raw_command=raw_command, source="compiler"))
    if module_key is None:
        return None

    from osah.domain.services.ai.detect_ai_command_track import _WRITE_VERB_PATTERN

    if not _WRITE_VERB_PATTERN.search(raw_command):
        return None

    intent_by_module = {
        "ppe": AiIntentKind.CREATE_PPE_ISSUANCE,
        "trainings": AiIntentKind.CREATE_TRAINING_RECORD,
        "medical": AiIntentKind.CREATE_MEDICAL_RECORD,
    }
    intent = intent_by_module.get(module_key)
    if intent is None:
        return None

    draft = AiCommandDraft(
        intent=intent,
        raw_command=raw_command,
        source="compiler",
        module_key=module_key,
        needs_confirmation=True,
    )
    return extract_write_slots(draft)


def _resolve_employee_reference(
    employee_query: str | None,
    personnel_number: str | None,
) -> tuple[str | None, str | None]:
    if personnel_number:
        return None, personnel_number.strip()
    if employee_query and employee_query.strip().isdigit():
        return None, employee_query.strip()
    return employee_query, personnel_number
