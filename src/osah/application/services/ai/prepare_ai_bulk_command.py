from pathlib import Path

from osah.application.services.ai.build_ai_bulk_confirmation_view import build_ai_bulk_confirmation_view
from osah.application.services.ai.resolve_ai_bulk_audience import resolve_ai_bulk_audience
from osah.application.services.ai.resolve_ai_entities import resolve_ppe_items_in_draft
from osah.domain.entities.ai_bulk_audience_resolution_status import AiBulkAudienceResolutionStatus
from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_entity_resolution_status import AiEntityResolutionStatus
from osah.domain.entities.ai_prepared_bulk_command import AiPreparedBulkCommand
from osah.domain.entities.ai_prepared_command_status import AiPreparedCommandStatus
from osah.domain.services.ai.validate_ai_bulk_operation import collect_ai_bulk_blocking_issues


def prepare_ai_bulk_command(database_path: Path, draft: AiCommandDraft) -> AiPreparedBulkCommand:
    """Готовит массовую AI-команду к preview и UI-подтверждению без Qt-зависимостей.
    Prepares a bulk AI command for preview and UI confirmation without Qt dependencies.
    """

    audience_resolution = resolve_ai_bulk_audience(database_path, draft)
    if audience_resolution.status == AiBulkAudienceResolutionStatus.NEEDS_CLARIFICATION:
        return AiPreparedBulkCommand(
            status=AiPreparedCommandStatus.NEEDS_CLARIFICATION,
            draft=audience_resolution.draft or draft,
            message=audience_resolution.message,
            choices=audience_resolution.choices,
            pending_employee_query=audience_resolution.pending_employee_query,
            pending_registry_choice_kind=audience_resolution.pending_registry_choice_kind,
        )
    if audience_resolution.status in {
        AiBulkAudienceResolutionStatus.EMPTY,
        AiBulkAudienceResolutionStatus.TOO_LARGE,
    }:
        return AiPreparedBulkCommand(
            status=AiPreparedCommandStatus.INVALID,
            draft=audience_resolution.draft or draft,
            message=audience_resolution.message,
        )

    resolved_draft = audience_resolution.draft or draft
    personnel_numbers = audience_resolution.personnel_numbers

    ppe_resolution = resolve_ppe_items_in_draft(database_path, resolved_draft)
    if ppe_resolution is not None:
        if ppe_resolution.status == AiEntityResolutionStatus.NEEDS_CLARIFICATION:
            return AiPreparedBulkCommand(
                status=AiPreparedCommandStatus.NEEDS_CLARIFICATION,
                draft=ppe_resolution.draft or resolved_draft,
                message=ppe_resolution.message,
                choices=ppe_resolution.choices,
                pending_ppe_item_index=ppe_resolution.pending_ppe_item_index,
            )
        if ppe_resolution.draft is not None:
            resolved_draft = ppe_resolution.draft

    blocking_issues = collect_ai_bulk_blocking_issues(database_path, resolved_draft, personnel_numbers)
    if blocking_issues:
        return AiPreparedBulkCommand(
            status=AiPreparedCommandStatus.INVALID,
            draft=resolved_draft,
            message="\n".join(blocking_issues[:5]),
            personnel_numbers=personnel_numbers,
        )

    confirmation_view = build_ai_bulk_confirmation_view(database_path, resolved_draft, personnel_numbers)
    return AiPreparedBulkCommand(
        status=AiPreparedCommandStatus.READY,
        draft=resolved_draft,
        personnel_numbers=personnel_numbers,
        confirmation_view=confirmation_view,
    )
