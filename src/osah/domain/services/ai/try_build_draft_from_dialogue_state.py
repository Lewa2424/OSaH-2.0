import re

from osah.domain.entities.ai_bulk_audience_spec import AiBulkAudienceSpec
from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_conversation_pending_kind import AiConversationPendingKind
from osah.domain.entities.ai_dialogue_state import AiDialogueState
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.services.ai.ai_relative_date_markers import mentions_current_date
from osah.domain.services.ai.detect_ai_command_track import extract_ppe_token_from_command
from osah.domain.services.ai.matches_audience_anaphora import matches_audience_anaphora
from osah.domain.services.ai.matches_department_list_follow_up import matches_department_list_follow_up
from osah.domain.services.ai.matches_department_problems_follow_up import matches_department_problems_follow_up
from osah.domain.services.ai.matches_department_readiness_follow_up import matches_department_readiness_follow_up
from osah.domain.services.ai.resolve_audience_subset_from_command import resolve_audience_subset_from_command

_BULK_PPE_WRITE_PATTERN = re.compile(
    r"\b(?:"
    r"занеси|занести|видай|выдай|выдать|дай|раздай|"
    r"впиши|выпиши|оформи|проведи|провести"
    r")\b",
    re.IGNORECASE,
)


def try_build_draft_from_dialogue_state(
    command_text: str,
    state: AiDialogueState | None,
    *,
    database_path=None,
) -> AiCommandDraft | None:
    """Будує чернетку зі стану діалогу для follow-up команд.
    Builds a command draft from dialogue state for follow-up commands.
    """

    if state is None:
        return None

    normalized = command_text.strip()
    if not normalized:
        return None

    if state.pending_kind == AiConversationPendingKind.DEPARTMENT_EMPLOYEES and state.department_query:
        if matches_department_list_follow_up(normalized):
            return AiCommandDraft(
                intent=AiIntentKind.QUERY_EMPLOYEES_FILTER,
                raw_command=normalized,
                source="dialogue_state",
                filter_key="department",
                department_query=state.department_query,
                employee_query=state.department_query,
                needs_confirmation=False,
            )
        if matches_department_problems_follow_up(normalized):
            return AiCommandDraft(
                intent=AiIntentKind.QUERY_MODULE_STATUS,
                raw_command=normalized,
                source="dialogue_state",
                module_key="trainings",
                filter_key="warning",
                department_query=state.department_query,
                needs_confirmation=False,
            )
        if matches_department_readiness_follow_up(normalized):
            return AiCommandDraft(
                intent=AiIntentKind.QUERY_EMPLOYEES_FILTER,
                raw_command=normalized,
                source="dialogue_state",
                filter_key="department",
                department_query=state.department_query,
                employee_query=state.department_query,
                needs_confirmation=False,
            )
        if _BULK_PPE_WRITE_PATTERN.search(normalized) and state.audience_personnel_numbers:
            return _build_bulk_ppe_draft(normalized, state, state.audience_personnel_numbers)

    if not state.audience_personnel_numbers:
        return None

    if not _BULK_PPE_WRITE_PATTERN.search(normalized):
        return None

    if database_path is None:
        if matches_audience_anaphora(normalized):
            return _build_bulk_ppe_draft(normalized, state, state.audience_personnel_numbers)
        return None

    subset = resolve_audience_subset_from_command(database_path, normalized, state)
    if subset is None:
        return None

    if subset.clarification_message and not subset.personnel_numbers:
        return AiCommandDraft(
            intent=AiIntentKind.BULK_CREATE_PPE_ISSUANCE,
            raw_command=normalized,
            source="dialogue_state",
            clarification_message=subset.clarification_message,
            needs_confirmation=True,
        )

    if not subset.personnel_numbers:
        return None

    draft = _build_bulk_ppe_draft(normalized, state, subset.personnel_numbers)
    if subset.clarification_message:
        draft = AiCommandDraft(
            intent=draft.intent,
            raw_command=draft.raw_command,
            source=draft.source,
            ppe_item_query=draft.ppe_item_query,
            issue_date=draft.issue_date,
            bulk_audience_spec=draft.bulk_audience_spec,
            needs_confirmation=draft.needs_confirmation,
            clarification_message=subset.clarification_message,
        )
    return draft


def _build_bulk_ppe_draft(
    normalized: str,
    state: AiDialogueState,
    personnel_numbers: tuple[str, ...],
) -> AiCommandDraft:
    ppe_item = extract_ppe_token_from_command(normalized) or state.ppe_item_query or "каска"
    issue_date = "сьогодні" if mentions_current_date(normalized) else None
    return AiCommandDraft(
        intent=AiIntentKind.BULK_CREATE_PPE_ISSUANCE,
        raw_command=normalized,
        source="dialogue_state",
        ppe_item_query=ppe_item,
        issue_date=issue_date,
        bulk_audience_spec=AiBulkAudienceSpec(
            resolved_personnel_numbers=personnel_numbers,
        ),
        needs_confirmation=True,
    )
