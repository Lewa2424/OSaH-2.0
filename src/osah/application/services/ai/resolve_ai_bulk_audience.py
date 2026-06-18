from dataclasses import replace
from pathlib import Path

from osah.application.services.ai.query_employees_by_filter import query_employees_by_filter
from osah.application.services.ai.resolve_department_from_registry import resolve_department_from_registry
from osah.application.services.ai.resolve_position_from_registry import resolve_position_from_registry
from osah.application.services.ai.search_employees_by_query import search_employees_by_query
from osah.application.services.load_employee_registry import load_employee_registry
from osah.application.services.load_work_permit_registry import load_work_permit_registry
from osah.domain.entities.ai_bulk_audience_resolution import AiBulkAudienceResolution
from osah.domain.entities.ai_bulk_audience_resolution_status import AiBulkAudienceResolutionStatus
from osah.domain.entities.ai_bulk_audience_row import AiBulkAudienceRow
from osah.domain.entities.ai_bulk_audience_spec import AiBulkAudienceSpec
from osah.domain.entities.ai_bulk_limits import AI_BULK_MAX_AUDIENCE_SIZE
from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.entities.ai_entity_choice import AiEntityChoice
from osah.domain.services.ai.build_registry_suggestion_clarification_message import (
    build_registry_suggestion_clarification_message,
)
from osah.domain.services.ai.filter_personnel_numbers_for_ppe_conditions import (
    filter_personnel_numbers_for_ppe_conditions,
)
from osah.domain.services.ai.has_bulk_audience_narrowing import has_bulk_audience_narrowing
from osah.domain.services.ai.match_department_name_query import department_name_matches_query
from osah.domain.services.ai.match_position_name_query import position_name_matches_query
from osah.domain.services.parse_service_date_text import parse_service_date_text
from osah.domain.services.parse_storage_datetime_text import parse_storage_datetime_text


def resolve_ai_bulk_audience(database_path: Path, draft: AiCommandDraft) -> AiBulkAudienceResolution:
    """Розв'язує аудиторію масової AI-команди з локальної БД.
    Resolves the bulk AI command audience from the local database.
    """

    audience_spec = draft.bulk_audience_spec
    if audience_spec is None:
        return AiBulkAudienceResolution(
            status=AiBulkAudienceResolutionStatus.EMPTY,
            message="Не вказано критерії аудиторії.",
            draft=draft,
        )

    if not has_bulk_audience_narrowing(audience_spec):
        return AiBulkAudienceResolution(
            status=AiBulkAudienceResolutionStatus.NEEDS_CLARIFICATION,
            message="Уточніть, для кого саме виконати масову дію.",
            draft=draft,
        )

    explicit_resolution, explicit_numbers = _resolve_explicit_employee_queries(database_path, draft, audience_spec)
    if explicit_resolution is not None:
        return explicit_resolution

    criterion_sets, registry_resolution = _collect_criterion_sets(database_path, audience_spec, explicit_numbers)
    if registry_resolution is not None:
        return registry_resolution
    if not criterion_sets:
        return AiBulkAudienceResolution(
            status=AiBulkAudienceResolutionStatus.EMPTY,
            message="За вказаними критеріями працівників не знайдено.",
            draft=draft,
        )

    personnel_numbers = _combine_personnel_numbers(audience_spec.combine_mode, criterion_sets)
    if draft.intent == AiIntentKind.BULK_CREATE_PPE_ISSUANCE:
        personnel_numbers = filter_personnel_numbers_for_ppe_conditions(
            database_path,
            draft,
            personnel_numbers,
        )
    if not personnel_numbers:
        return AiBulkAudienceResolution(
            status=AiBulkAudienceResolutionStatus.EMPTY,
            message="За вказаними критеріями працівників не знайдено.",
            draft=draft,
        )

    if len(personnel_numbers) > AI_BULK_MAX_AUDIENCE_SIZE:
        return AiBulkAudienceResolution(
            status=AiBulkAudienceResolutionStatus.TOO_LARGE,
            message=(
                f"Знайдено {len(personnel_numbers)} працівників. "
                f"Максимум за одну команду — {AI_BULK_MAX_AUDIENCE_SIZE}. Звужте критерії."
            ),
            draft=draft,
            personnel_numbers=personnel_numbers,
        )

    rows = _build_audience_rows(database_path, personnel_numbers)
    updated_draft = replace(draft, resolved_audience=personnel_numbers)
    return AiBulkAudienceResolution(
        status=AiBulkAudienceResolutionStatus.READY,
        message=f"Готово до підтвердження: {len(personnel_numbers)} працівників.",
        draft=updated_draft,
        rows=rows,
        personnel_numbers=personnel_numbers,
    )


def apply_bulk_audience_employee_choice(
    draft: AiCommandDraft,
    *,
    pending_employee_query: str,
    choice_id: str,
) -> AiCommandDraft:
    """Додає вибраного працівника до resolved-аудиторії після уточнення.
    Adds a selected employee to the resolved audience after clarification.
    """

    audience_spec = draft.bulk_audience_spec
    if audience_spec is None:
        return draft

    remaining_queries = tuple(
        query for query in audience_spec.employee_queries if query.strip().lower() != pending_employee_query.strip().lower()
    )
    resolved_numbers = tuple(dict.fromkeys((*audience_spec.resolved_personnel_numbers, choice_id.strip())))
    updated_spec = replace(
        audience_spec,
        employee_queries=remaining_queries,
        resolved_personnel_numbers=resolved_numbers,
    )
    return replace(draft, bulk_audience_spec=updated_spec)


def _resolve_explicit_employee_queries(
    database_path: Path,
    draft: AiCommandDraft,
    audience_spec: AiBulkAudienceSpec,
) -> tuple[AiBulkAudienceResolution | None, frozenset[str]]:
    if not audience_spec.employee_queries:
        return None, frozenset(audience_spec.resolved_personnel_numbers)

    resolved_numbers = list(audience_spec.resolved_personnel_numbers)
    for employee_query in audience_spec.employee_queries:
        matches = search_employees_by_query(database_path, employee_query)
        if not matches:
            continue
        if len(matches) > 1:
            choices = tuple(
                AiEntityChoice(
                    choice_id=employee.personnel_number,
                    label=f"{employee.full_name} ({employee.personnel_number})",
                    personnel_number=employee.personnel_number,
                )
                for employee in matches[:10]
            )
            return (
                AiBulkAudienceResolution(
                    status=AiBulkAudienceResolutionStatus.NEEDS_CLARIFICATION,
                    message=f"Знайдено кілька збігів для «{employee_query}». Оберіть працівника.",
                    draft=draft,
                    choices=choices,
                    pending_employee_query=employee_query,
                ),
                frozenset(),
            )
        resolved_numbers.append(matches[0].personnel_number)

    explicit_numbers = frozenset(resolved_numbers)
    if audience_spec.employee_queries and not explicit_numbers:
        return (
            AiBulkAudienceResolution(
                status=AiBulkAudienceResolutionStatus.EMPTY,
                message="За вказаними ПІБ/таб.№ працівників не знайдено.",
                draft=draft,
            ),
            frozenset(),
        )

    if audience_spec.employee_queries and not _has_non_explicit_criteria(audience_spec):
        personnel_numbers = tuple(sorted(explicit_numbers))
        if len(personnel_numbers) > AI_BULK_MAX_AUDIENCE_SIZE:
            return (
                AiBulkAudienceResolution(
                    status=AiBulkAudienceResolutionStatus.TOO_LARGE,
                    message=f"Знайдено {len(personnel_numbers)} працівників. Максимум — {AI_BULK_MAX_AUDIENCE_SIZE}.",
                    draft=draft,
                ),
                frozenset(),
            )
        rows = _build_audience_rows(database_path, personnel_numbers)
        updated_draft = replace(draft, resolved_audience=personnel_numbers)
        return (
            AiBulkAudienceResolution(
                status=AiBulkAudienceResolutionStatus.READY,
                message=f"Готово до підтвердження: {len(personnel_numbers)} працівників.",
                draft=updated_draft,
                rows=rows,
                personnel_numbers=personnel_numbers,
            ),
            frozenset(),
        )

    return None, explicit_numbers


def _has_non_explicit_criteria(audience_spec: AiBulkAudienceSpec) -> bool:
    return any(
        (
            audience_spec.department_query,
            audience_spec.position_query,
            audience_spec.filter_key,
            audience_spec.permit_number,
            audience_spec.arrived_from,
            audience_spec.arrived_until,
        )
    )


def _collect_criterion_sets(
    database_path: Path,
    audience_spec: AiBulkAudienceSpec,
    explicit_numbers: frozenset[str],
) -> tuple[list[frozenset[str]], AiBulkAudienceResolution | None]:
    criterion_sets: list[frozenset[str]] = []

    if explicit_numbers:
        criterion_sets.append(explicit_numbers)

    if audience_spec.resolved_personnel_numbers and not explicit_numbers:
        criterion_sets.append(frozenset(audience_spec.resolved_personnel_numbers))

    if audience_spec.department_query:
        department_set, department_resolution = _collect_by_department_registry(database_path, audience_spec.department_query)
        if department_resolution is not None:
            return [], department_resolution
        if department_set:
            criterion_sets.append(department_set)

    if audience_spec.position_query:
        position_set, position_resolution = _collect_by_position_registry(database_path, audience_spec.position_query)
        if position_resolution is not None:
            return [], position_resolution
        if position_set:
            criterion_sets.append(position_set)

    if audience_spec.filter_key:
        filter_set = frozenset(row.personnel_number for row in query_employees_by_filter(database_path, audience_spec.filter_key))
        if filter_set:
            criterion_sets.append(filter_set)

    if audience_spec.permit_number:
        permit_set = _collect_permit_participants(database_path, audience_spec.permit_number)
        if permit_set:
            criterion_sets.append(permit_set)

    if audience_spec.arrived_from or audience_spec.arrived_until:
        arrived_set = _collect_by_arrived_range(database_path, audience_spec.arrived_from, audience_spec.arrived_until)
        if arrived_set:
            criterion_sets.append(arrived_set)

    return criterion_sets, None


def _combine_personnel_numbers(combine_mode: str, criterion_sets: list[frozenset[str]]) -> tuple[str, ...]:
    if not criterion_sets:
        return ()

    if combine_mode == "or":
        combined: set[str] = set()
        for criterion_set in criterion_sets:
            combined.update(criterion_set)
        return tuple(sorted(combined))

    combined_set = set(criterion_sets[0])
    for criterion_set in criterion_sets[1:]:
        combined_set &= criterion_set
    return tuple(sorted(combined_set))


def _collect_by_department_registry(
    database_path: Path,
    department_query: str,
) -> tuple[frozenset[str] | None, AiBulkAudienceResolution | None]:
    resolution = resolve_department_from_registry(database_path, department_query)
    if resolution.status == "ambiguous":
        choices = tuple(
            AiEntityChoice(choice_id=name, label=name, choice_kind="department")
            for name in resolution.candidates[:10]
        )
        return None, AiBulkAudienceResolution(
            status=AiBulkAudienceResolutionStatus.NEEDS_CLARIFICATION,
            message="Знайдено кілька варіантів підрозділу. Оберіть потрібний.",
            choices=choices,
            pending_registry_choice_kind="department",
        )
    if resolution.status == "suggest":
        choices = tuple(
            AiEntityChoice(choice_id=name, label=name, choice_kind="department")
            for name in resolution.candidates[:10]
        )
        return None, AiBulkAudienceResolution(
            status=AiBulkAudienceResolutionStatus.NEEDS_CLARIFICATION,
            message=build_registry_suggestion_clarification_message(department_query, label="підрозділ"),
            choices=choices,
            pending_registry_choice_kind="department",
        )
    if resolution.status == "not_found":
        return frozenset(), None
    if resolution.status == "resolved" and resolution.canonical_name:
        return _collect_by_department_exact(database_path, resolution.canonical_name), None
    if resolution.status == "empty":
        return None, None
    return _collect_by_department(database_path, department_query), None


def _collect_by_position_registry(
    database_path: Path,
    position_query: str,
) -> tuple[frozenset[str] | None, AiBulkAudienceResolution | None]:
    resolution = resolve_position_from_registry(database_path, position_query)
    if resolution.status == "ambiguous":
        choices = tuple(
            AiEntityChoice(choice_id=name, label=name, choice_kind="position")
            for name in resolution.candidates[:10]
        )
        return None, AiBulkAudienceResolution(
            status=AiBulkAudienceResolutionStatus.NEEDS_CLARIFICATION,
            message="Знайдено кілька варіантів посади. Оберіть потрібну.",
            choices=choices,
            pending_registry_choice_kind="position",
        )
    if resolution.status == "suggest":
        choices = tuple(
            AiEntityChoice(choice_id=name, label=name, choice_kind="position")
            for name in resolution.candidates[:10]
        )
        return None, AiBulkAudienceResolution(
            status=AiBulkAudienceResolutionStatus.NEEDS_CLARIFICATION,
            message=build_registry_suggestion_clarification_message(position_query, label="посада"),
            choices=choices,
            pending_registry_choice_kind="position",
        )
    if resolution.status == "not_found":
        return frozenset(), None
    if resolution.status == "resolved" and resolution.canonical_name:
        return _collect_by_position_exact(database_path, resolution.canonical_name), None
    if resolution.status == "empty":
        return None, None
    return _collect_by_position(database_path, position_query), None


def _collect_by_department_exact(database_path: Path, department_name: str) -> frozenset[str]:
    normalized = department_name.strip().lower()
    return frozenset(
        employee.personnel_number
        for employee in load_employee_registry(database_path)
        if (employee.department_name or "").strip().lower() == normalized
    )


def _collect_by_position_exact(database_path: Path, position_name: str) -> frozenset[str]:
    normalized = position_name.strip().lower()
    return frozenset(
        employee.personnel_number
        for employee in load_employee_registry(database_path)
        if (employee.position_name or "").strip().lower() == normalized
    )


def _collect_by_department(database_path: Path, department_query: str) -> frozenset[str]:
    return frozenset(
        employee.personnel_number
        for employee in load_employee_registry(database_path)
        if department_name_matches_query(employee.department_name, department_query)
    )


def _collect_by_position(database_path: Path, position_query: str) -> frozenset[str]:
    return frozenset(
        employee.personnel_number
        for employee in load_employee_registry(database_path)
        if position_name_matches_query(employee.position_name, position_query)
    )


def _collect_permit_participants(database_path: Path, permit_number: str) -> frozenset[str]:
    normalized = permit_number.strip().lstrip("№")
    for permit in load_work_permit_registry(database_path):
        if permit.permit_number.strip().lstrip("№") == normalized:
            return frozenset(participant.employee_personnel_number for participant in permit.participants)
    return frozenset()


def _collect_by_arrived_range(
    database_path: Path,
    arrived_from: str | None,
    arrived_until: str | None,
) -> frozenset[str]:
    from_date = parse_service_date_text(arrived_from) if arrived_from else None
    until_date = parse_service_date_text(arrived_until) if arrived_until else None
    matched: set[str] = set()
    for employee in load_employee_registry(database_path):
        if not employee.created_at_text:
            continue
        try:
            created_at = parse_storage_datetime_text(employee.created_at_text)
        except ValueError:
            continue
        if from_date is not None and created_at.date() < from_date:
            continue
        if until_date is not None and created_at.date() > until_date:
            continue
        matched.add(employee.personnel_number)
    return frozenset(matched)


def _build_audience_rows(database_path: Path, personnel_numbers: tuple[str, ...]) -> tuple[AiBulkAudienceRow, ...]:
    employees_by_number = {
        employee.personnel_number: employee for employee in load_employee_registry(database_path)
    }
    rows: list[AiBulkAudienceRow] = []
    for personnel_number in personnel_numbers:
        employee = employees_by_number.get(personnel_number)
        full_name = employee.full_name if employee is not None else "Невідомий працівник"
        rows.append(AiBulkAudienceRow(personnel_number=personnel_number, full_name=full_name))
    return tuple(rows)
