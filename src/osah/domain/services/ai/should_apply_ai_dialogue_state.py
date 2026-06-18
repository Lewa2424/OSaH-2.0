import re

from osah.domain.entities.ai_conversation_pending_kind import AiConversationPendingKind
from osah.domain.entities.ai_dialogue_state import AiDialogueState
from osah.domain.services.ai.extract_employee_queries_from_command import extract_employee_queries_from_command
from osah.domain.services.ai.extract_short_name_follow_up import extract_short_name_follow_up
from osah.domain.services.ai.matches_audience_anaphora import matches_audience_anaphora
from osah.domain.services.ai.matches_audience_pronoun import matches_audience_pronoun
from osah.domain.services.ai.matches_department_list_follow_up import matches_department_list_follow_up
from osah.domain.services.ai.matches_department_problems_follow_up import matches_department_problems_follow_up
from osah.domain.services.ai.matches_department_readiness_follow_up import matches_department_readiness_follow_up

_BULK_PPE_WRITE_PATTERN = re.compile(
    r"\b(?:"
    r"занеси|занести|видай|выдай|выдать|дай|раздай|"
    r"впиши|выпиши|оформи|проведи|провести"
    r")\b",
    re.IGNORECASE,
)


def should_apply_ai_dialogue_state(
    state: AiDialogueState | None,
    command_text: str,
) -> bool:
    """Визначає, чи наступна команда має злитись із збереженим станом діалогу.
    Decides whether the next command should merge with stored dialogue state.
    """

    if state is None:
        return False

    normalized = command_text.strip()
    if not normalized:
        return False

    if state.pending_kind == AiConversationPendingKind.DEPARTMENT_EMPLOYEES and state.department_query:
        if (
            matches_department_list_follow_up(normalized)
            or matches_department_problems_follow_up(normalized)
            or matches_department_readiness_follow_up(normalized)
        ):
            return True

    if not state.audience_personnel_numbers:
        return False

    if matches_audience_anaphora(normalized):
        return True

    if matches_audience_pronoun(normalized):
        return True

    if extract_short_name_follow_up(normalized) is not None:
        return True

    if _BULK_PPE_WRITE_PATTERN.search(normalized) and extract_employee_queries_from_command(normalized):
        return True

    return False
