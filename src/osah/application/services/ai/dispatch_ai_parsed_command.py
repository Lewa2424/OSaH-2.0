from dataclasses import replace
from pathlib import Path

from osah.application.services.ai.build_ai_operation_plan import build_ai_operation_plan
from osah.application.services.ai.build_ai_query_answer import build_ai_query_answer
from osah.application.services.ai.build_ai_read_navigation_target import build_ai_read_navigation_target
from osah.application.services.ai.resolve_ai_entities import resolve_ai_entities
from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_dispatch_result import AiDispatchResult
from osah.domain.entities.ai_dispatch_result_kind import AiDispatchResultKind
from osah.domain.entities.ai_entity_resolution_status import AiEntityResolutionStatus
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.entities.ai_operation_plan_kind import AiOperationPlanKind
from osah.domain.entities.ai_ui_context import AiUiContext


def dispatch_ai_parsed_command(
    database_path: Path,
    draft: AiCommandDraft,
    *,
    ui_context: AiUiContext | None = None,
) -> AiDispatchResult:
    """Маршрутизирует разобранную AI-команду без Qt-зависимостей.
    Routes a parsed AI command without Qt dependencies.
    """

    operation_plan = build_ai_operation_plan(draft, database_path=database_path)
    planned_draft = operation_plan.draft
    if not operation_plan.can_execute:
        message = "\n".join(operation_plan.issues) or "Я поки не вмію безпечно виконати таку команду."
        return AiDispatchResult(kind=AiDispatchResultKind.UNSUPPORTED, draft=planned_draft, message=message)

    if operation_plan.kind == AiOperationPlanKind.ANSWER:
        return _dispatch_answer(database_path, planned_draft, ui_context=ui_context)

    if operation_plan.kind == AiOperationPlanKind.NAVIGATION:
        return _dispatch_navigation(database_path, planned_draft, ui_context=ui_context)

    if operation_plan.kind == AiOperationPlanKind.BULK_WRITE:
        return AiDispatchResult(kind=AiDispatchResultKind.BULK_REQUIRED, draft=planned_draft)

    if operation_plan.kind == AiOperationPlanKind.SINGLE_WRITE:
        return AiDispatchResult(kind=AiDispatchResultKind.WRITE_REQUIRED, draft=planned_draft)

    message = "\n".join(operation_plan.issues) or "Я поки не вмію безпечно виконати таку команду."
    return AiDispatchResult(kind=AiDispatchResultKind.UNSUPPORTED, draft=planned_draft, message=message)


def _dispatch_answer(
    database_path: Path,
    draft: AiCommandDraft,
    *,
    ui_context: AiUiContext | None,
) -> AiDispatchResult:
    """Готовит read-only ответ или запрос уточнения сущности.
    Prepares a read-only answer or an entity clarification request.
    """

    resolved_draft = draft
    if draft.intent in {AiIntentKind.QUERY_EMPLOYEE_READINESS, AiIntentKind.QUERY_EMPLOYEE_RECORDS}:
        entity_resolution = _resolve_employee_for_answer(database_path, draft)
        if isinstance(entity_resolution, AiDispatchResult):
            return entity_resolution
        resolved_draft = entity_resolution

    if draft.intent == AiIntentKind.QUERY_MISSING_PPE and draft.employee_query:
        entity_resolution = resolve_ai_entities(database_path, draft)
        if entity_resolution.status == AiEntityResolutionStatus.NEEDS_CLARIFICATION:
            return AiDispatchResult(
                kind=AiDispatchResultKind.ENTITY_CHOICES_REQUIRED,
                draft=draft,
                message=entity_resolution.message,
                choices=entity_resolution.choices,
                pending_ppe_item_index=entity_resolution.pending_ppe_item_index,
                pending_answer_mode=True,
            )
        if entity_resolution.status == AiEntityResolutionStatus.NOT_FOUND:
            return AiDispatchResult(
                kind=AiDispatchResultKind.NOT_FOUND,
                draft=draft,
                message=entity_resolution.message,
                pending_answer_mode=True,
            )
        if entity_resolution.draft is not None:
            resolved_draft = entity_resolution.draft

    answer = build_ai_query_answer(database_path, resolved_draft, ui_context=ui_context)
    if answer is None:
        return AiDispatchResult(
            kind=AiDispatchResultKind.UNSUPPORTED,
            draft=resolved_draft,
            message="Я зрозумів запит, але поки не вмію сформувати таку відповідь.",
        )

    return AiDispatchResult(
        kind=AiDispatchResultKind.ANSWER_READY,
        draft=resolved_draft,
        answer_text=answer.text,
        follow_up_navigation=answer.follow_up_navigation,
        allow_copy=answer.allow_copy,
        pending_answer_mode=True,
    )


def _dispatch_navigation(
    database_path: Path,
    draft: AiCommandDraft,
    *,
    ui_context: AiUiContext | None,
) -> AiDispatchResult:
    """Готовит цель навигации или запрос уточнения сущности.
    Prepares a navigation target or an entity clarification request.
    """

    resolved_draft = draft
    if draft.intent == AiIntentKind.OPEN_EMPLOYEE_CARD and draft.employee_query and not draft.personnel_number:
        entity_resolution = resolve_ai_entities(database_path, draft)
        if entity_resolution.status == AiEntityResolutionStatus.NEEDS_CLARIFICATION:
            return AiDispatchResult(
                kind=AiDispatchResultKind.ENTITY_CHOICES_REQUIRED,
                draft=draft,
                message=entity_resolution.message,
                choices=entity_resolution.choices,
            )
        if entity_resolution.status == AiEntityResolutionStatus.NOT_FOUND:
            return AiDispatchResult(kind=AiDispatchResultKind.NOT_FOUND, draft=draft, message=entity_resolution.message)
        if entity_resolution.draft is not None:
            resolved_draft = entity_resolution.draft

    target = build_ai_read_navigation_target(resolved_draft, ui_context=ui_context)
    if target is None:
        return AiDispatchResult(
            kind=AiDispatchResultKind.UNSUPPORTED,
            draft=resolved_draft,
            message="Я зрозумів запит, але поки не вмію відкрити такий екран.",
        )

    return AiDispatchResult(kind=AiDispatchResultKind.NAVIGATION_READY, draft=resolved_draft, navigation_target=target)


def _resolve_employee_for_answer(database_path: Path, draft: AiCommandDraft) -> AiCommandDraft | AiDispatchResult:
    """Возвращает уточнение или черновик с найденным сотрудником для read-only ответа.
    Returns clarification or a draft with a resolved employee for a read-only answer.
    """

    if not draft.employee_query or draft.personnel_number:
        return draft

    entity_resolution = resolve_ai_entities(database_path, draft)
    if entity_resolution.status == AiEntityResolutionStatus.NEEDS_CLARIFICATION:
        return AiDispatchResult(
            kind=AiDispatchResultKind.ENTITY_CHOICES_REQUIRED,
            draft=draft,
            message=entity_resolution.message,
            choices=entity_resolution.choices,
            pending_answer_mode=True,
        )
    if entity_resolution.status == AiEntityResolutionStatus.NOT_FOUND:
        return AiDispatchResult(
            kind=AiDispatchResultKind.NOT_FOUND,
            draft=draft,
            message=entity_resolution.message,
            pending_answer_mode=True,
        )
    if entity_resolution.draft is not None:
        return entity_resolution.draft
    if entity_resolution.resolved_personnel_number:
        return replace(draft, personnel_number=entity_resolution.resolved_personnel_number)
    return draft
