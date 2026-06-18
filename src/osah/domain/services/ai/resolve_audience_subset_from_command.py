from dataclasses import dataclass
from pathlib import Path

from osah.domain.entities.ai_dialogue_state import AiDialogueState
from osah.domain.entities.employee import Employee
from osah.domain.services.ai.extract_employee_queries_from_command import extract_employee_queries_from_command
from osah.domain.services.ai.match_employees_by_name_query import match_employees_by_name_query
from osah.domain.services.ai.matches_audience_anaphora import matches_audience_anaphora
from osah.domain.services.ai.matches_audience_pronoun import matches_audience_pronoun
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.list_employees import list_employees


@dataclass(frozen=True, slots=True)
class AudienceSubsetResolution:
    """Результат звуження аудиторії діалогу за командою.
    Result of narrowing dialogue audience by command.
    """

    personnel_numbers: tuple[str, ...]
    last_mentioned_personnel_number: str | None = None
    outside_audience_labels: tuple[str, ...] = ()
    clarification_message: str | None = None


def resolve_audience_subset_from_command(
    database_path: Path,
    command_text: str,
    state: AiDialogueState,
) -> AudienceSubsetResolution | None:
    """Звужує аудиторію діалогу за іменами, анафорою або займенником.
    Narrows dialogue audience by names, anaphora or pronoun reference.
    """

    audience_numbers = state.audience_personnel_numbers
    if not audience_numbers:
        return None

    normalized = command_text.strip()
    if not normalized:
        return None

    audience_employees = _load_audience_employees(database_path, audience_numbers)

    if matches_audience_anaphora(normalized):
        return AudienceSubsetResolution(personnel_numbers=audience_numbers)

    if matches_audience_pronoun(normalized) and state.last_mentioned_personnel_number:
        if state.last_mentioned_personnel_number in audience_numbers:
            return AudienceSubsetResolution(
                personnel_numbers=(state.last_mentioned_personnel_number,),
                last_mentioned_personnel_number=state.last_mentioned_personnel_number,
            )

    name_queries = extract_employee_queries_from_command(normalized)
    if not name_queries:
        return None

    resolved_numbers: list[str] = []
    outside_labels: list[str] = []
    last_mentioned: str | None = None

    for query_text in name_queries:
        audience_matches = match_employees_by_name_query(audience_employees, query_text)
        if audience_matches:
            for employee in audience_matches:
                if employee.personnel_number not in resolved_numbers:
                    resolved_numbers.append(employee.personnel_number)
                    last_mentioned = employee.personnel_number
            continue

        global_matches = match_employees_by_name_query(
            _load_all_employees(database_path),
            query_text,
        )
        if global_matches:
            outside_labels.append(global_matches[0].full_name)
        else:
            outside_labels.append(query_text)

    if not resolved_numbers:
        if outside_labels:
            labels = ", ".join(outside_labels)
            return AudienceSubsetResolution(
                personnel_numbers=(),
                outside_audience_labels=tuple(outside_labels),
                clarification_message=(
                    f"«{labels}» не входять до попереднього списку. "
                    "Уточніть, кому саме видати, або назвіть іншого працівника зі списку."
                ),
            )
        return None

    clarification = None
    if outside_labels:
        labels = ", ".join(outside_labels)
        clarification = (
            f"Увага: «{labels}» не в попередньому списку. "
            "Підготовлено видачу лише для знайдених у списку працівників."
        )

    return AudienceSubsetResolution(
        personnel_numbers=tuple(resolved_numbers),
        last_mentioned_personnel_number=last_mentioned,
        outside_audience_labels=tuple(outside_labels),
        clarification_message=clarification,
    )


def _load_audience_employees(
    database_path: Path,
    personnel_numbers: tuple[str, ...],
) -> tuple[Employee, ...]:
    allowed = set(personnel_numbers)
    return tuple(employee for employee in _load_all_employees(database_path) if employee.personnel_number in allowed)


def _load_all_employees(database_path: Path) -> tuple[Employee, ...]:
    connection = create_database_connection(database_path)
    try:
        return tuple(list_employees(connection))
    finally:
        connection.close()
