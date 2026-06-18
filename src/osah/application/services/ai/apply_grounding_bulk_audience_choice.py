from dataclasses import replace

from osah.domain.entities.ai_bulk_audience_spec import AiBulkAudienceSpec
from osah.domain.entities.ai_command_draft import AiCommandDraft


def apply_grounding_bulk_audience_choice(
    draft: AiCommandDraft,
    choice_id: str,
    *,
    choice_kind: str,
) -> AiCommandDraft:
    """Підставляє канонічну назву в bulk_audience_spec після ambiguous grounding.
    Applies a canonical registry name into bulk_audience_spec after ambiguous grounding.
    """

    canonical = choice_id.strip()
    spec = draft.bulk_audience_spec
    if spec is None:
        if choice_kind == "department":
            return replace(draft, department_query=canonical)
        if choice_kind == "position":
            return replace(draft, position_query=canonical)
        return draft

    if choice_kind == "department":
        updated_spec = replace(spec, department_query=canonical, position_query=None)
    elif choice_kind == "position":
        updated_spec = replace(spec, position_query=canonical, department_query=None)
    else:
        return draft
    return replace(draft, bulk_audience_spec=updated_spec)
