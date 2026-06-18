from dataclasses import replace
from pathlib import Path

from osah.application.services.ai.resolve_department_from_registry import resolve_department_from_registry
from osah.application.services.ai.resolve_employee_from_registry import resolve_employee_from_registry
from osah.application.services.ai.resolve_position_from_registry import resolve_position_from_registry
from osah.application.services.ai.resolve_ai_entities import (
    _employee_choices_from_full_names,
    resolve_ai_entities,
)
from osah.domain.entities.ai_bulk_audience_spec import AiBulkAudienceSpec
from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_entity_choice import AiEntityChoice
from osah.domain.entities.ai_entity_resolution_status import AiEntityResolutionStatus
from osah.domain.entities.ai_grounding_result import AiGroundingResult
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.services.ai.build_registry_suggestion_clarification_message import (
    build_registry_not_found_clarification_message,
    build_registry_suggestion_clarification_message,
)


def effective_department_query(draft: AiCommandDraft) -> str | None:
    """Повертає фрагмент підрозділу з чернетки з урахуванням зворотної сумісності.
    Returns the department query fragment from a draft with backward compatibility.
    """

    if draft.department_query and draft.department_query.strip():
        return draft.department_query.strip()
    if (draft.filter_key or "").strip().lower() == "department":
        employee_query = (draft.employee_query or "").strip()
        return employee_query or None
    if draft.intent == AiIntentKind.QUERY_MODULE_STATUS:
        employee_query = (draft.employee_query or "").strip()
        return employee_query or None
    return None


def ground_ai_command_draft(database_path: Path, draft: AiCommandDraft) -> AiGroundingResult:
    """Зіставляє span-поля чернетки з реєстром БД.
    Grounds draft span fields against the database registry.
    """

    enriched = draft

    if draft.intent == AiIntentKind.QUERY_MISSING_PPE:
        ppe_resolution = resolve_ai_entities(database_path, draft)
        if ppe_resolution.status == AiEntityResolutionStatus.NEEDS_CLARIFICATION:
            return AiGroundingResult(
                ok=False,
                draft=draft,
                message=ppe_resolution.message,
                choices=ppe_resolution.choices,
                choice_kind="ppe_item",
            )
        if ppe_resolution.draft is not None:
            enriched = ppe_resolution.draft

    department_query = effective_department_query(enriched)
    if department_query:
        department_result = _ground_department_with_position_retry(
            database_path,
            department_query,
        )
        if department_result is not None:
            if not department_result.ok:
                return AiGroundingResult(
                    ok=False,
                    draft=enriched,
                    message=department_result.message,
                    choices=department_result.choices,
                    choice_kind=department_result.choice_kind,
                )
            if (department_result.draft.department_query or "").strip():
                canonical = department_result.draft.department_query.strip()
                replace_kwargs: dict[str, object] = {"department_query": canonical}
                filter_key = (enriched.filter_key or "").strip().lower()
                if filter_key == "department":
                    replace_kwargs["employee_query"] = None
                elif enriched.intent == AiIntentKind.QUERY_MODULE_STATUS:
                    replace_kwargs["employee_query"] = None
                enriched = replace(enriched, **replace_kwargs)
            elif (department_result.draft.position_query or "").strip():
                canonical = department_result.draft.position_query.strip()
                enriched = replace(
                    enriched,
                    department_query=None,
                    position_query=canonical,
                )

    position_query = (enriched.position_query or "").strip()
    if position_query:
        position_result = _ground_registry_value(
            database_path,
            position_query,
            resolver=resolve_position_from_registry,
            label="посада",
            choice_kind="position",
        )
        if position_result is not None:
            if not position_result.ok:
                return AiGroundingResult(
                    ok=False,
                    draft=enriched,
                    message=position_result.message,
                    choices=position_result.choices,
                    choice_kind=position_result.choice_kind,
                )
            canonical = (position_result.draft.position_query or "").strip()
            enriched = replace(enriched, position_query=canonical)

    employee_query = (enriched.employee_query or "").strip()
    if (
        employee_query
        and not (enriched.personnel_number or "").strip()
        and enriched.intent != AiIntentKind.EXPLAIN_HELP
    ):
        employee_result = _ground_employee_value(
            database_path,
            employee_query,
            raw_command=enriched.raw_command,
        )
        if employee_result is not None:
            if not employee_result.ok:
                return AiGroundingResult(
                    ok=False,
                    draft=enriched,
                    message=employee_result.message,
                    choices=employee_result.choices,
                    choice_kind=employee_result.choice_kind,
                )
            enriched = replace(
                enriched,
                employee_query=employee_result.draft.employee_query,
                personnel_number=employee_result.draft.personnel_number,
            )

    if enriched.bulk_audience_spec is not None:
        grounded_spec = _ground_bulk_audience_spec(database_path, enriched.bulk_audience_spec)
        if isinstance(grounded_spec, AiGroundingResult):
            return grounded_spec
        enriched = replace(enriched, bulk_audience_spec=grounded_spec)

    return AiGroundingResult(ok=True, draft=enriched)


def _ground_bulk_audience_spec(
    database_path: Path,
    spec: AiBulkAudienceSpec,
) -> AiBulkAudienceSpec | AiGroundingResult:
    """Зіставляє department/position у bulk_audience_spec з реєстром.
    Grounds department/position fields inside bulk_audience_spec against the registry.
    """

    updated = spec
    position_query = (spec.position_query or "").strip()
    if position_query:
        position_result = _ground_registry_value(
            database_path,
            position_query,
            resolver=resolve_position_from_registry,
            label="посада",
            choice_kind="position",
        )
        if position_result is not None:
            if not position_result.ok:
                return position_result
            canonical = (position_result.draft.position_query or "").strip()
            updated = replace(updated, position_query=canonical, department_query=None)
        return updated

    department_query = (spec.department_query or "").strip()
    if department_query:
        department_result = _ground_department_with_position_retry(
            database_path,
            department_query,
        )
        if department_result is not None:
            if not department_result.ok:
                return department_result
            if (department_result.draft.department_query or "").strip():
                canonical = department_result.draft.department_query.strip()
                updated = replace(updated, department_query=canonical, position_query=None)
            elif (department_result.draft.position_query or "").strip():
                canonical = department_result.draft.position_query.strip()
                updated = replace(updated, department_query=None, position_query=canonical)

    return updated


def _ground_registry_value(
    database_path: Path,
    query: str,
    *,
    resolver,
    label: str,
    choice_kind: str,
) -> AiGroundingResult | None:
    resolution = resolver(database_path, query)
    if resolution.status == "empty":
        return None
    if resolution.status == "suggest":
        choices = tuple(
            AiEntityChoice(choice_id=name, label=name, choice_kind=choice_kind)
            for name in resolution.candidates[:10]
        )
        return AiGroundingResult(
            ok=False,
            draft=AiCommandDraft(
                intent=AiIntentKind.UNKNOWN,
                raw_command="",
                source="grounding",
            ),
            message=build_registry_suggestion_clarification_message(query, label=label),
            choices=choices,
            choice_kind=choice_kind,
        )
    if resolution.status == "not_found":
        return AiGroundingResult(
            ok=False,
            draft=AiCommandDraft(
                intent=AiIntentKind.UNKNOWN,
                raw_command="",
                source="grounding",
            ),
            message=build_registry_not_found_clarification_message(query, label=label),
        )
    if resolution.status == "ambiguous":
        choices = tuple(
            AiEntityChoice(choice_id=name, label=name, choice_kind=choice_kind)
            for name in resolution.candidates[:10]
        )
        return AiGroundingResult(
            ok=False,
            draft=AiCommandDraft(
                intent=AiIntentKind.UNKNOWN,
                raw_command="",
                source="grounding",
            ),
            message=f"Знайдено кілька варіантів ({label}). Оберіть потрібний.",
            choices=choices,
            choice_kind=choice_kind,
        )
    canonical = resolution.canonical_name
    if not canonical:
        return None
    if choice_kind == "department":
        return AiGroundingResult(
            ok=True,
            draft=AiCommandDraft(
                intent=AiIntentKind.UNKNOWN,
                raw_command="",
                source="grounding",
                department_query=canonical,
            ),
        )
    return AiGroundingResult(
        ok=True,
        draft=AiCommandDraft(
            intent=AiIntentKind.UNKNOWN,
            raw_command="",
            source="grounding",
            position_query=canonical,
        ),
    )


def _ground_department_with_position_retry(
    database_path: Path,
    query: str,
) -> AiGroundingResult | None:
    """Зіставляє підрозділ; при невдачі пробує той самий фрагмент як посаду.
    Grounds a department query; on failure retries the same fragment as position.
    """

    department_result = _ground_registry_value(
        database_path,
        query,
        resolver=resolve_department_from_registry,
        label="підрозділ",
        choice_kind="department",
    )
    if department_result is None or department_result.ok:
        return department_result

    position_result = _ground_registry_value(
        database_path,
        query,
        resolver=resolve_position_from_registry,
        label="посада",
        choice_kind="position",
    )
    if position_result is not None and (position_result.ok or position_result.choices):
        return position_result
    return department_result


def _ground_employee_value(
    database_path: Path,
    query: str,
    *,
    raw_command: str,
) -> AiGroundingResult | None:
    """Зіставляє фрагмент ПІБ із реєстром працівників.
    Grounds an employee name fragment against the employee registry.
    """

    resolution = resolve_employee_from_registry(
        database_path,
        query,
        raw_command=raw_command,
    )
    if resolution.status == "empty":
        return None
    if resolution.status == "suggest":
        choices = _employee_choices_from_full_names(database_path, resolution.candidates)
        return AiGroundingResult(
            ok=False,
            draft=AiCommandDraft(
                intent=AiIntentKind.UNKNOWN,
                raw_command="",
                source="grounding",
            ),
            message=build_registry_suggestion_clarification_message(query, label="працівника"),
            choices=choices,
            choice_kind="employee",
        )
    if resolution.status == "not_found":
        return AiGroundingResult(
            ok=False,
            draft=AiCommandDraft(
                intent=AiIntentKind.UNKNOWN,
                raw_command="",
                source="grounding",
            ),
            message=build_registry_not_found_clarification_message(query, label="працівника"),
            choice_kind="employee",
        )
    if resolution.status == "ambiguous":
        choices = _employee_choices_from_full_names(database_path, resolution.candidates)
        return AiGroundingResult(
            ok=False,
            draft=AiCommandDraft(
                intent=AiIntentKind.UNKNOWN,
                raw_command="",
                source="grounding",
            ),
            message="Знайдено кілька працівників. Оберіть потрібного.",
            choices=choices,
            choice_kind="employee",
        )
    if resolution.status == "resolved":
        return AiGroundingResult(
            ok=True,
            draft=AiCommandDraft(
                intent=AiIntentKind.UNKNOWN,
                raw_command="",
                source="grounding",
                employee_query=resolution.canonical_name,
                personnel_number=resolution.resolved_personnel_number,
            ),
        )
    return None
