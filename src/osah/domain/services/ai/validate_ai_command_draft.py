from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.entities.ai_item_draft import AiItemDraft
from osah.domain.services.ai.ensure_ai_intent_is_allowed import is_ai_answer_intent, is_ai_bulk_intent, is_ai_navigation_intent, is_ai_write_intent
from osah.domain.services.ai.build_unknown_intent_clarification_message import build_unknown_intent_clarification_message


def validate_ai_command_draft(draft: AiCommandDraft) -> list[str]:
    """Перевіряє чернетку AI перед показом підтвердження.
    Validates an AI draft before confirmation UI.
    """

    if draft.clarification_message:
        return [draft.clarification_message]

    issues: list[str] = []

    if draft.intent == AiIntentKind.UNKNOWN:
        issues.append(build_unknown_intent_clarification_message(draft.raw_command))

    if is_ai_navigation_intent(draft.intent):
        if draft.intent == AiIntentKind.OPEN_EMPLOYEE_CARD and not (draft.personnel_number or draft.employee_query):
            issues.append("Потрібен працівник або табельний номер.")
        if draft.intent == AiIntentKind.NAVIGATE_SECTION and not draft.section_key:
            issues.append("Потрібен цільовий розділ.")
        return issues

    if is_ai_answer_intent(draft.intent):
        if draft.intent == AiIntentKind.QUERY_MISSING_PPE and not (draft.ppe_item_query or "").strip():
            issues.append("Потрібно вказати предмет ЗІЗ.")
        if draft.intent == AiIntentKind.QUERY_EMPLOYEE_READINESS and not (
            draft.personnel_number or draft.employee_query
        ):
            issues.append("Потрібен працівник або табельний номер.")
        if draft.intent == AiIntentKind.QUERY_EMPLOYEE_RECORDS and not (
            draft.personnel_number or draft.employee_query
        ):
            issues.append("Потрібен працівник або табельний номер.")
        if draft.intent == AiIntentKind.QUERY_WORK_PERMIT_READINESS and not (
            draft.permit_number or draft.permit_query
        ):
            issues.append("Потрібен номер наряду.")
        if draft.intent == AiIntentKind.QUERY_MODULE_STATUS and not (
            (draft.module_key or draft.section_key) and draft.filter_key
        ):
            issues.append("Потрібен модуль і статус для спискового запиту.")
        return issues

    if not is_ai_write_intent(draft.intent):
        return issues

    if is_ai_bulk_intent(draft.intent):
        _validate_bulk_write(draft, issues)
        return issues

    if draft.intent == AiIntentKind.CREATE_PPE_ISSUANCE:
        _validate_create_ppe(draft, issues)
    elif draft.intent == AiIntentKind.CREATE_TRAINING_RECORD:
        _validate_employee_and_date(draft, issues)
    elif draft.intent == AiIntentKind.CREATE_MEDICAL_RECORD:
        _validate_employee_and_date(draft, issues)
    elif draft.intent == AiIntentKind.UPDATE_PPE_RECORD:
        _validate_employee_and_date(draft, issues, date_required=False)
        if not draft.items and not draft.ppe_item_query:
            issues.append("Потрібно вказати предмет ЗІЗ для оновлення.")
    elif draft.intent == AiIntentKind.UPDATE_TRAINING_RECORD:
        _validate_employee_and_date(draft, issues, date_required=False)
    elif draft.intent == AiIntentKind.UPDATE_MEDICAL_RECORD:
        _validate_employee_and_date(draft, issues, date_required=False)
    elif draft.intent == AiIntentKind.UPDATE_EMPLOYEE_FIELDS:
        if not draft.employee_query and not draft.personnel_number:
            issues.append("Потрібно вказати працівника.")
        if draft.employee_field_updates is None:
            issues.append("Потрібно вказати поле для оновлення.")
    elif draft.intent == AiIntentKind.CREATE_WORK_PERMIT_DRAFT:
        if not (draft.permit_number or draft.permit_query):
            issues.append("Потрібен номер наряду.")
        if not draft.work_kind:
            issues.append("Потрібно вказати вид робіт.")
        if not draft.starts_at_text or not draft.ends_at_text:
            issues.append("Потрібно вказати час початку та завершення.")
    elif draft.intent in {AiIntentKind.ADD_WORK_PERMIT_PARTICIPANT, AiIntentKind.REMOVE_WORK_PERMIT_PARTICIPANT}:
        if not (draft.permit_number or draft.permit_query):
            issues.append("Потрібен номер наряду.")
        if not draft.employee_query and not draft.personnel_number:
            issues.append("Потрібно вказати учасника.")

    return issues


def _validate_create_ppe(draft: AiCommandDraft, issues: list[str]) -> None:
    if not draft.employee_query and not draft.personnel_number:
        issues.append("Потрібно вказати працівника.")
    if not draft.items:
        issues.append("Потрібно вказати хоча б один предмет ЗІЗ.")
    if not draft.issue_date:
        issues.append("Потрібно вказати дату видачі.")
    for item in draft.items:
        if not item.name.strip():
            issues.append("Назва предмета ЗІЗ не може бути порожньою.")
        if item.quantity <= 0:
            issues.append("Кількість ЗІЗ має бути більше нуля.")


def _validate_employee_and_date(
    draft: AiCommandDraft,
    issues: list[str],
    *,
    date_required: bool = True,
) -> None:
    if not draft.employee_query and not draft.personnel_number:
        issues.append("Потрібно вказати працівника.")
    if date_required and not draft.issue_date:
        issues.append("Потрібно вказати дату.")


def normalize_ai_item_drafts(raw_items: object) -> tuple[AiItemDraft, ...]:
    """Нормалізує список предметів із JSON LLM.
    Normalizes item list parsed from LLM JSON.
    """

    if not isinstance(raw_items, list):
        return ()

    normalized_items: list[AiItemDraft] = []
    for raw_item in raw_items:
        if not isinstance(raw_item, dict):
            continue
        raw_name = raw_item.get("name")
        raw_quantity = raw_item.get("quantity", 1)
        if not isinstance(raw_name, str):
            continue
        quantity = int(raw_quantity) if isinstance(raw_quantity, (int, float, str)) and str(raw_quantity).isdigit() else 1
        normalized_items.append(AiItemDraft(name=raw_name.strip(), quantity=quantity))

    return tuple(normalized_items)


def _validate_bulk_write(draft: AiCommandDraft, issues: list[str]) -> None:
    if draft.bulk_audience_spec is None:
        issues.append("Потрібно вказати аудиторію масової дії.")
    if draft.intent == AiIntentKind.BULK_CREATE_PPE_ISSUANCE:
        if not draft.items and not draft.ppe_item_query:
            issues.append("Потрібно вказати предмет ЗІЗ.")
        if not draft.issue_date:
            issues.append("Потрібно вказати дату видачі.")
    elif draft.intent == AiIntentKind.BULK_CREATE_TRAINING_RECORD:
        if not draft.issue_date:
            issues.append("Потрібно вказати дату інструктажу.")
    elif draft.intent == AiIntentKind.BULK_CREATE_MEDICAL_RECORD:
        if not draft.issue_date:
            issues.append("Потрібно вказати дату медогляду.")
    elif draft.intent == AiIntentKind.BULK_UPDATE_EMPLOYEE_FIELDS:
        if draft.employee_field_updates is None:
            issues.append("Потрібно вказати поле для оновлення.")
    elif draft.intent == AiIntentKind.BULK_ADD_WORK_PERMIT_PARTICIPANTS:
        permit_number = draft.permit_number
        if draft.bulk_audience_spec is not None and draft.bulk_audience_spec.permit_number:
            permit_number = permit_number or draft.bulk_audience_spec.permit_number
        if not permit_number:
            issues.append("Потрібен номер наряду.")
