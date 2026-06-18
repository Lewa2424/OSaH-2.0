from dataclasses import replace
from pathlib import Path

from osah.application.services.ai.resolve_employee_from_registry import resolve_employee_from_registry
from osah.application.services.ai.resolve_ppe_catalog_item import resolve_ppe_catalog_item
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.list_employees import list_employees
from osah.application.services.ai.search_ppe_catalog_candidates import search_ppe_catalog_candidates
from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_entity_choice import AiEntityChoice
from osah.domain.entities.ai_entity_resolution import AiEntityResolution
from osah.domain.entities.ai_entity_resolution_status import AiEntityResolutionStatus
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.entities.ai_item_draft import AiItemDraft
from osah.domain.services.ai.build_registry_suggestion_clarification_message import (
    build_registry_suggestion_clarification_message,
)
from osah.domain.services.ai.command_verb_tokens import sanitize_employee_query


def resolve_ai_entities(database_path: Path, draft: AiCommandDraft) -> AiEntityResolution:
    """Розв'язує сутності AI-команди після парсингу.
    Resolves AI command entities after parsing.
    """

    if draft.intent == AiIntentKind.QUERY_MISSING_PPE:
        ppe_resolution = _resolve_missing_ppe_query(database_path, draft)
        if ppe_resolution is not None:
            return ppe_resolution

    if draft.intent == AiIntentKind.QUERY_MODULE_STATUS:
        return AiEntityResolution(status=AiEntityResolutionStatus.READY, draft=draft)

    if draft.intent in {
        AiIntentKind.CREATE_WORK_PERMIT_DRAFT,
        AiIntentKind.QUERY_WORK_PERMIT_READINESS,
        AiIntentKind.QUERY_WORK_PERMIT_LIST,
    } and (draft.permit_number or draft.permit_query):
        return AiEntityResolution(status=AiEntityResolutionStatus.READY, draft=draft)

    if draft.intent == AiIntentKind.CREATE_WORK_PERMIT_DRAFT:
        return AiEntityResolution(status=AiEntityResolutionStatus.READY, draft=draft)

    if draft.personnel_number:
        ppe_resolution = _resolve_ppe_items(database_path, draft)
        if ppe_resolution is not None:
            return ppe_resolution
        return AiEntityResolution(
            status=AiEntityResolutionStatus.READY,
            draft=draft,
            resolved_personnel_number=draft.personnel_number,
        )

    employee_query = sanitize_employee_query((draft.employee_query or "").strip()) or ""
    if not employee_query:
        ppe_resolution = _resolve_ppe_items(database_path, draft)
        if ppe_resolution is not None:
            return ppe_resolution
        return AiEntityResolution(
            status=AiEntityResolutionStatus.READY,
            draft=draft,
            resolved_personnel_number=draft.personnel_number,
        )

    resolution = resolve_employee_from_registry(
        database_path,
        employee_query,
        raw_command=draft.raw_command,
    )
    if resolution.status == "resolved":
        resolved_draft = replace(
            draft,
            personnel_number=resolution.resolved_personnel_number,
            employee_query=resolution.canonical_name,
        )
        ppe_resolution = _resolve_ppe_items(database_path, resolved_draft)
        if ppe_resolution is not None:
            return ppe_resolution
        return AiEntityResolution(
            status=AiEntityResolutionStatus.READY,
            draft=resolved_draft,
            resolved_personnel_number=resolution.resolved_personnel_number,
        )

    if resolution.status in {"suggest", "ambiguous"}:
        choices = _employee_choices_from_full_names(database_path, resolution.candidates)
        if choices:
            message = (
                build_registry_suggestion_clarification_message(employee_query, label="працівника")
                if resolution.status == "suggest"
                else "Знайдено кілька працівників. Оберіть потрібного кнопкою нижче."
            )
            return AiEntityResolution(
                status=AiEntityResolutionStatus.NEEDS_CLARIFICATION,
                message=message,
                draft=draft,
                choices=choices,
            )

    return AiEntityResolution(
        status=AiEntityResolutionStatus.NOT_FOUND,
        message=f"Працівника '{employee_query}' не знайдено.",
        draft=draft,
    )


def apply_selected_entity_choice(draft: AiCommandDraft, choice_id: str) -> AiCommandDraft:
    """Підставляє вибраного працівника у чернетку AI-команди.
    Applies the selected employee into the AI command draft.
    """

    return replace(
        draft,
        personnel_number=choice_id.strip(),
        employee_query=None,
    )


def apply_selected_ppe_item_choice(draft: AiCommandDraft, item_index: int, ppe_name: str) -> AiCommandDraft:
    """Підставляє вибрану назву ЗІЗ у чернетку AI-команди.
    Applies the selected PPE item name into the AI command draft.
    """

    if draft.intent == AiIntentKind.QUERY_MISSING_PPE:
        return replace(draft, ppe_item_query=ppe_name.strip())

    updated_items: list[AiItemDraft] = []
    for index, item in enumerate(draft.items):
        if index == item_index:
            updated_items.append(AiItemDraft(name=ppe_name.strip(), quantity=item.quantity))
        else:
            updated_items.append(item)
    return replace(draft, items=tuple(updated_items))


def _resolve_missing_ppe_query(database_path: Path, draft: AiCommandDraft) -> AiEntityResolution | None:
    ppe_item_query = (draft.ppe_item_query or "").strip()
    if not ppe_item_query:
        return None
    candidates = search_ppe_catalog_candidates(database_path, ppe_item_query)
    if len(candidates) > 1:
        choices = tuple(
            AiEntityChoice(
                choice_id=candidate_name,
                label=candidate_name,
                choice_kind="ppe_item",
            )
            for candidate_name in candidates
        )
        return AiEntityResolution(
            status=AiEntityResolutionStatus.NEEDS_CLARIFICATION,
            message=build_registry_suggestion_clarification_message(ppe_item_query, label="ЗІЗ"),
            draft=draft,
            choices=choices,
            pending_ppe_item_index=0,
        )
    if candidates:
        return AiEntityResolution(
            status=AiEntityResolutionStatus.READY,
            draft=replace(draft, ppe_item_query=candidates[0]),
        )
    return AiEntityResolution(
        status=AiEntityResolutionStatus.READY,
        draft=draft,
    )


def _resolve_ppe_items(database_path: Path, draft: AiCommandDraft) -> AiEntityResolution | None:
    return resolve_ppe_items_in_draft(database_path, draft)


def resolve_ppe_items_in_draft(database_path: Path, draft: AiCommandDraft) -> AiEntityResolution | None:
    """Розв'язує назви предметів ЗІЗ у single/bulk write-чернетці.
    Resolves PPE item names in a single or bulk write draft.
    """

    if draft.intent not in {AiIntentKind.CREATE_PPE_ISSUANCE, AiIntentKind.BULK_CREATE_PPE_ISSUANCE}:
        return None
    if not draft.items:
        return None

    resolved_items: list[AiItemDraft] = []
    for index, item in enumerate(draft.items):
        candidates = search_ppe_catalog_candidates(database_path, item.name)
        if len(candidates) > 1:
            choices = tuple(
                AiEntityChoice(
                    choice_id=candidate_name,
                    label=candidate_name,
                    choice_kind="ppe_item",
                )
                for candidate_name in candidates
            )
            return AiEntityResolution(
                status=AiEntityResolutionStatus.NEEDS_CLARIFICATION,
                message=build_registry_suggestion_clarification_message(item.name, label="ЗІЗ"),
                draft=draft,
                choices=choices,
                pending_ppe_item_index=index,
            )
        resolved_items.append(
            AiItemDraft(
                name=resolve_ppe_catalog_item(database_path, item.name) or item.name,
                quantity=item.quantity,
            )
        )

    return AiEntityResolution(
        status=AiEntityResolutionStatus.READY,
        draft=replace(draft, items=tuple(resolved_items)),
        resolved_personnel_number=draft.personnel_number,
    )


def _employee_choices_from_full_names(
    database_path: Path,
    full_names: tuple[str, ...],
) -> tuple[AiEntityChoice, ...]:
    """Будує варіанти вибору працівника за повними ПІБ з реєстру.
    Builds employee choice options from full names in the registry.
    """

    if not full_names:
        return ()

    connection = create_database_connection(database_path)
    try:
        employees_by_name = {
            employee.full_name.strip().lower(): employee
            for employee in list_employees(connection)
        }
    finally:
        connection.close()

    choices: list[AiEntityChoice] = []
    for full_name in full_names[:10]:
        employee = employees_by_name.get(full_name.strip().lower())
        if employee is None:
            continue
        choices.append(
            AiEntityChoice(
                choice_id=employee.personnel_number,
                label=f"{employee.full_name}, таб. №{employee.personnel_number}",
                personnel_number=employee.personnel_number,
                choice_kind="employee",
            )
        )
    return tuple(choices)
