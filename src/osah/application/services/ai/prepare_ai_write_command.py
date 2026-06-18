from dataclasses import replace
from pathlib import Path

from osah.application.services.ai.build_ai_confirmation_view import build_ai_confirmation_view
from osah.application.services.ai.execute_confirmed_ai_command import build_employee_label
from osah.application.services.ai.preflight_ai_command_draft import preflight_ai_command_draft
from osah.application.services.ai.resolve_ai_entities import resolve_ai_entities
from osah.application.services.ai.resolve_ai_record_for_update import resolve_ai_record_for_update
from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_entity_resolution_status import AiEntityResolutionStatus
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.entities.ai_prepared_command_status import AiPreparedCommandStatus
from osah.domain.entities.ai_prepared_write_command import AiPreparedWriteCommand
from osah.domain.services.ai.compiler.compile_ai_command import compile_ai_command


def prepare_ai_write_command(database_path: Path, draft: AiCommandDraft) -> AiPreparedWriteCommand:
    """Готовит одиночную write-команду к UI-подтверждению без Qt-зависимостей.
    Prepares a single write command for UI confirmation without Qt dependencies.
    """

    compiled_draft = compile_ai_command(draft).draft
    if compiled_draft.intent == AiIntentKind.CREATE_WORK_PERMIT_DRAFT:
        return _build_ready_result(database_path, compiled_draft, personnel_number=None)

    entity_resolution = resolve_ai_entities(database_path, compiled_draft)
    if entity_resolution.status == AiEntityResolutionStatus.NEEDS_CLARIFICATION:
        return AiPreparedWriteCommand(
            status=AiPreparedCommandStatus.NEEDS_CLARIFICATION,
            draft=entity_resolution.draft or compiled_draft,
            message=entity_resolution.message,
            choices=entity_resolution.choices,
            pending_ppe_item_index=entity_resolution.pending_ppe_item_index,
        )
    if entity_resolution.status == AiEntityResolutionStatus.NOT_FOUND:
        return AiPreparedWriteCommand(
            status=AiPreparedCommandStatus.NOT_FOUND,
            draft=compiled_draft,
            message=entity_resolution.message,
        )

    resolved_draft = entity_resolution.draft or compiled_draft
    personnel_number = entity_resolution.resolved_personnel_number
    if not personnel_number:
        return AiPreparedWriteCommand(
            status=AiPreparedCommandStatus.INVALID,
            draft=resolved_draft,
            message="Не вдалося визначити працівника.",
        )

    if resolved_draft.intent in {
        AiIntentKind.UPDATE_PPE_RECORD,
        AiIntentKind.UPDATE_TRAINING_RECORD,
        AiIntentKind.UPDATE_MEDICAL_RECORD,
    }:
        record_target = resolve_ai_record_for_update(
            database_path,
            resolved_draft,
            personnel_number=personnel_number,
        )
        if record_target is None:
            return AiPreparedWriteCommand(
                status=AiPreparedCommandStatus.INVALID,
                draft=resolved_draft,
                message="Запис для оновлення не знайдено або знайдено кілька збігів.",
                personnel_number=personnel_number,
            )

    return _build_ready_result(database_path, resolved_draft, personnel_number=personnel_number)


def _build_ready_result(
    database_path: Path,
    draft: AiCommandDraft,
    *,
    personnel_number: str | None,
) -> AiPreparedWriteCommand:
    """Собирает preflight и confirmation preview для одиночной write-команды.
    Builds preflight and confirmation preview for a single write command.
    """

    preflight = preflight_ai_command_draft(
        draft,
        database_path=database_path,
        resolved_personnel_number=personnel_number,
    )
    enriched_draft = preflight.enriched_draft
    employee_label = build_employee_label(database_path, personnel_number) if personnel_number else ""
    confirmation_view = build_ai_confirmation_view(
        enriched_draft,
        employee_label=employee_label,
        resolved_personnel_number=personnel_number,
        database_path=database_path,
    )
    if preflight.warnings and not confirmation_view.warning_text:
        confirmation_view = replace(confirmation_view, warning_text=preflight.warnings[0])
    if not preflight.ok:
        return AiPreparedWriteCommand(
            status=AiPreparedCommandStatus.INVALID,
            draft=enriched_draft,
            message="\n".join(preflight.issues),
            personnel_number=personnel_number,
            confirmation_view=confirmation_view,
        )
    return AiPreparedWriteCommand(
        status=AiPreparedCommandStatus.READY,
        draft=enriched_draft,
        personnel_number=personnel_number,
        confirmation_view=confirmation_view,
    )
