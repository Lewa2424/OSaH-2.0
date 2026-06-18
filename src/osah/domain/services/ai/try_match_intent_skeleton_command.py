from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.services.ai.detect_ai_command_track import extract_ppe_token_from_command
from osah.domain.services.ai.extract_position_span_from_command import extract_position_span_from_command
from osah.domain.services.ai.matches_missing_ppe_list_query import matches_missing_ppe_list_query
from osah.domain.services.ai.try_match_department_combo_query import try_match_department_combo_query
from osah.domain.services.ai.try_match_department_employees_query import try_match_department_employees_query


def try_match_intent_skeleton_command(command_text: str) -> AiCommandDraft | None:
    """Повертає чернетку за маркерами наміру без LLM і без regex на назви з БД.
    Returns a draft from intent markers without LLM or enterprise-value regex.
    """

    normalized = command_text.strip()
    if not normalized:
        return None

    combo = try_match_department_combo_query(normalized)
    if combo is not None:
        return combo

    department_draft = try_match_department_employees_query(normalized)
    if department_draft is not None:
        return department_draft

    if matches_missing_ppe_list_query(normalized):
        ppe_token = extract_ppe_token_from_command(normalized) or "каска"
        position_query = extract_position_span_from_command(normalized)
        return AiCommandDraft(
            intent=AiIntentKind.QUERY_MISSING_PPE,
            raw_command=normalized,
            source="intent_skeleton",
            ppe_item_query=ppe_token,
            position_query=position_query,
            needs_confirmation=False,
        )

    return None
