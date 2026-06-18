from enum import StrEnum


class AiSemanticConditionType(StrEnum):
    """Условие безопасного выполнения AI-команды.
    Safe execution condition for an AI command.
    """

    SKIP_IF_ACTIVE_PPE_EXISTS = "skip_if_active_ppe_exists"
    ONLY_IF_WORK_PERMIT_IS_DRAFT = "only_if_work_permit_is_draft"
    DO_NOT_CHANGE_POSITION = "do_not_change_position"
    DO_NOT_DELETE_EXISTING_RECORD = "do_not_delete_existing_record"
    UNTIL_NEXT_MEDICAL_EXAM = "until_next_medical_exam"
