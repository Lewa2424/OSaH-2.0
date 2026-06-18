from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.entities.ai_pending_slot_kind import AiPendingSlotKind
from osah.domain.entities.training_type import TrainingType
from osah.domain.services.ai.ensure_ai_intent_is_allowed import is_ai_bulk_intent, is_ai_write_intent
from osah.domain.services.ai.has_bulk_audience_narrowing import has_bulk_audience_narrowing
from osah.domain.services.ai.normalize_ai_training_type import normalize_ai_training_type


def list_missing_slots(draft: AiCommandDraft) -> tuple[AiPendingSlotKind, ...]:
    """Повертає недостатні слоти для intent перед confirm.
    Returns missing slots for the intent before confirmation.
    """

    if draft.clarification_message:
        return ()

    if is_ai_bulk_intent(draft.intent):
        return _missing_bulk_slots(draft)

    if not is_ai_write_intent(draft.intent):
        return ()

    if draft.intent == AiIntentKind.CREATE_PPE_ISSUANCE:
        return _missing_create_ppe_slots(draft)
    if draft.intent == AiIntentKind.CREATE_TRAINING_RECORD:
        return _missing_create_training_slots(draft)
    if draft.intent == AiIntentKind.CREATE_MEDICAL_RECORD:
        return _missing_create_medical_slots(draft)
    return ()


def session_prompt_for_slot(slot: AiPendingSlotKind) -> str:
    """Повертає підказку користувачу для уточнення слота.
    Returns a user-facing prompt for slot clarification.
    """

    prompts = {
        AiPendingSlotKind.EMPLOYEE: "Вкажіть працівника (ПІБ або табельний номер).",
        AiPendingSlotKind.WORK_RISK_CATEGORY: (
            "Для розрахунку наступного повторного інструктажу потрібно обрати категорію робіт "
            "(небезпечні / звичайні)."
        ),
        AiPendingSlotKind.PPE_ITEM: "Вкажіть предмет ЗІЗ.",
        AiPendingSlotKind.BULK_AUDIENCE: (
            "Уточніть аудиторію: вкажіть ПІБ/таб.№, дільницю, посаду, наряд або інший критерій звуження."
        ),
        AiPendingSlotKind.ISSUE_DATE: "Вкажіть дату проведення або видачі.",
        AiPendingSlotKind.TRAINING_TYPE: "Вкажіть тип інструктажу.",
    }
    return prompts.get(slot, "Уточніть команду.")


def _missing_bulk_slots(draft: AiCommandDraft) -> tuple[AiPendingSlotKind, ...]:
    if draft.bulk_audience_spec is None or not has_bulk_audience_narrowing(draft.bulk_audience_spec):
        return (AiPendingSlotKind.BULK_AUDIENCE,)
    if draft.intent == AiIntentKind.BULK_CREATE_PPE_ISSUANCE and not draft.items and not draft.ppe_item_query:
        return (AiPendingSlotKind.PPE_ITEM,)
    if draft.intent == AiIntentKind.BULK_CREATE_TRAINING_RECORD and not draft.issue_date:
        return (AiPendingSlotKind.ISSUE_DATE,)
    return ()


def _missing_create_ppe_slots(draft: AiCommandDraft) -> tuple[AiPendingSlotKind, ...]:
    missing: list[AiPendingSlotKind] = []
    if not draft.personnel_number and not draft.employee_query:
        missing.append(AiPendingSlotKind.EMPLOYEE)
    if not draft.items and not draft.ppe_item_query:
        missing.append(AiPendingSlotKind.PPE_ITEM)
    if not draft.issue_date:
        missing.append(AiPendingSlotKind.ISSUE_DATE)
    return tuple(missing)


def _missing_create_training_slots(draft: AiCommandDraft) -> tuple[AiPendingSlotKind, ...]:
    missing: list[AiPendingSlotKind] = []
    if not draft.personnel_number and not draft.employee_query:
        missing.append(AiPendingSlotKind.EMPLOYEE)
    if not draft.issue_date:
        missing.append(AiPendingSlotKind.ISSUE_DATE)

    training_type = normalize_ai_training_type(draft.training_type)
    if training_type == TrainingType.REPEATED.value:
        needs_risk = (
            not draft.use_manual_next_control_date
            and not (draft.next_control_date or "").strip()
            and (draft.work_risk_category or "not_applicable") == "not_applicable"
        )
        if needs_risk:
            missing.append(AiPendingSlotKind.WORK_RISK_CATEGORY)
    return tuple(missing)


def _missing_create_medical_slots(draft: AiCommandDraft) -> tuple[AiPendingSlotKind, ...]:
    missing: list[AiPendingSlotKind] = []
    if not draft.personnel_number and not draft.employee_query:
        missing.append(AiPendingSlotKind.EMPLOYEE)
    if not draft.issue_date:
        missing.append(AiPendingSlotKind.ISSUE_DATE)
    return tuple(missing)
