from dataclasses import replace

from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_command_session import AiCommandSession
from osah.domain.entities.ai_compile_result import AiCompileResult
from osah.domain.entities.ai_pending_slot_kind import AiPendingSlotKind
from osah.domain.services.ai.compiler.ai_slot_normalizers import (
    extract_work_risk_category_from_command,
    normalize_work_risk_category_from_text,
    parse_relative_period_from_command,
)
from osah.domain.services.ai.compiler.compile_ai_command import compile_ai_command
from osah.domain.services.ai.extract_employee_query_from_command import (
    extract_employee_query_from_command,
    extract_personnel_number_from_command,
)
from osah.domain.services.ai.normalize_ai_issue_date_text import normalize_ai_issue_date_text
from osah.domain.services.ai.normalize_ai_training_type import normalize_ai_training_type


def fill_ai_command_session(session: AiCommandSession, answer_text: str) -> AiCompileResult:
    """Заповнює перший відсутній слот відповіддю користувача без LLM.
    Fills the first missing slot from user answer without LLM.
    """

    if not session.missing_slots:
        return compile_ai_command(session.draft)

    slot = session.missing_slots[0]
    draft = _apply_slot_answer(session.draft, slot, answer_text.strip())
    return compile_ai_command(draft)


def _apply_slot_answer(draft: AiCommandDraft, slot: AiPendingSlotKind, answer_text: str) -> AiCommandDraft:
    if not answer_text:
        return draft

    if slot == AiPendingSlotKind.WORK_RISK_CATEGORY:
        category = (
            normalize_work_risk_category_from_text(answer_text)
            or extract_work_risk_category_from_command(answer_text)
        )
        if category:
            return replace(draft, work_risk_category=category)
        return draft

    if slot == AiPendingSlotKind.EMPLOYEE:
        personnel_number = extract_personnel_number_from_command(answer_text)
        employee_query = extract_employee_query_from_command(answer_text)
        if personnel_number:
            return replace(draft, personnel_number=personnel_number, employee_query=None)
        if employee_query:
            return replace(draft, employee_query=employee_query)
        return replace(draft, employee_query=answer_text)

    if slot == AiPendingSlotKind.ISSUE_DATE:
        return replace(draft, issue_date=normalize_ai_issue_date_text(answer_text))

    if slot == AiPendingSlotKind.PPE_ITEM:
        from osah.domain.entities.ai_item_draft import AiItemDraft

        return replace(
            draft,
            ppe_item_query=answer_text,
            items=(AiItemDraft(name=answer_text, quantity=1),),
        )

    if slot == AiPendingSlotKind.TRAINING_TYPE:
        return replace(draft, training_type=normalize_ai_training_type(answer_text))

    if slot == AiPendingSlotKind.BULK_AUDIENCE:
        merged_command = f"{draft.raw_command} {answer_text}".strip()
        merged_draft = replace(draft, raw_command=merged_command)
        return compile_ai_command(merged_draft)

    next_control, use_manual = parse_relative_period_from_command(answer_text)
    if next_control:
        return replace(
            draft,
            next_control_date=next_control,
            use_manual_next_control_date=use_manual,
        )
    return draft
