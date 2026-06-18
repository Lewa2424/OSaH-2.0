from pathlib import Path

from osah.application.services.ai.preflight_ai_command_draft import preflight_ai_command_draft
from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.entities.ai_operation_plan import AiOperationPlan
from osah.domain.entities.ai_operation_plan_kind import AiOperationPlanKind
from osah.domain.entities.ai_semantic_mode import AiSemanticMode
from osah.domain.services.ai.has_bulk_audience_narrowing import has_bulk_audience_narrowing
from osah.domain.services.ai.ensure_ai_intent_is_allowed import (
    ensure_ai_intent_is_allowed,
    is_ai_answer_intent,
    is_ai_bulk_intent,
    is_ai_navigation_intent,
    is_ai_write_intent,
)


def build_ai_operation_plan(
    draft: AiCommandDraft,
    *,
    database_path: Path | None = None,
) -> AiOperationPlan:
    """Будує план безпечної обробки AI-команди перед UI-рішенням.
    Builds a safe AI command handling plan before the UI decision.
    """

    try:
        ensure_ai_intent_is_allowed(draft.intent)
    except ValueError as error:
        return AiOperationPlan(
            kind=AiOperationPlanKind.UNSUPPORTED,
            mode=AiSemanticMode.UNSUPPORTED,
            draft=draft,
            can_execute=False,
            issues=(str(error),),
        )

    if draft.clarification_message:
        return AiOperationPlan(
            kind=AiOperationPlanKind.UNSUPPORTED,
            mode=AiSemanticMode.UNSUPPORTED,
            draft=draft,
            can_execute=False,
            issues=(draft.clarification_message,),
        )

    if is_ai_navigation_intent(draft.intent):
        return AiOperationPlan(
            kind=AiOperationPlanKind.NAVIGATION,
            mode=AiSemanticMode.READ_ONLY,
            draft=draft,
        )

    if is_ai_answer_intent(draft.intent):
        return AiOperationPlan(
            kind=AiOperationPlanKind.ANSWER,
            mode=AiSemanticMode.READ_ONLY,
            draft=draft,
        )

    if is_ai_bulk_intent(draft.intent):
        preflight = preflight_ai_command_draft(draft, database_path=database_path)
        enriched_draft = preflight.enriched_draft
        audience_spec = enriched_draft.bulk_audience_spec
        issues: tuple[str, ...] = ()
        if audience_spec is None or not has_bulk_audience_narrowing(audience_spec):
            issues = (
                "Уточніть аудиторію: вкажіть ПІБ/таб.№, дільницю, посаду, наряд або інший критерій звуження.",
            )
        return AiOperationPlan(
            kind=AiOperationPlanKind.BULK_WRITE,
            mode=AiSemanticMode.PREVIEW_THEN_CONFIRM,
            draft=enriched_draft,
            requires_confirmation=True,
            requires_preview=True,
            can_execute=not issues,
            issues=issues,
            warnings=preflight.warnings,
        )

    if is_ai_write_intent(draft.intent):
        mode = _mode_for_single_write(draft)
        preflight = preflight_ai_command_draft(draft, database_path=database_path)
        return AiOperationPlan(
            kind=AiOperationPlanKind.SINGLE_WRITE,
            mode=mode,
            draft=preflight.enriched_draft,
            requires_confirmation=True,
            requires_preview=mode == AiSemanticMode.DRAFT_ONLY,
            can_execute=True,
            issues=(),
            warnings=preflight.warnings,
        )

    return AiOperationPlan(
        kind=AiOperationPlanKind.UNSUPPORTED,
        mode=AiSemanticMode.UNSUPPORTED,
        draft=draft,
        can_execute=False,
        issues=("Намір команди не має безпечного маршруту виконання.",),
    )


def _mode_for_single_write(draft: AiCommandDraft) -> AiSemanticMode:
    if draft.intent == AiIntentKind.CREATE_WORK_PERMIT_DRAFT:
        return AiSemanticMode.DRAFT_ONLY
    return AiSemanticMode.CONFIRM_THEN_EXECUTE
