from dataclasses import dataclass
from pathlib import Path

from osah.application.services.load_dashboard_snapshot_from_path import load_dashboard_snapshot_from_path
from osah.application.services.load_employee_workspace import load_employee_workspace
from osah.domain.entities.employee_status_level import EmployeeStatusLevel


@dataclass(slots=True, frozen=True)
class DailyFocusProblemRow:
    """Короткий рядок проблеми для фокусу дня.
    Short problem row for the daily focus answer.
    """

    employee_name: str
    personnel_number: str
    title: str
    detail: str


@dataclass(slots=True, frozen=True)
class DailyFocusQueryResult:
    """Результат запиту «що закрити сьогодні».
    Result of the daily focus query.
    """

    focus_text: str
    problems: tuple[DailyFocusProblemRow, ...]


def query_daily_focus(database_path: Path, *, limit: int = 10) -> DailyFocusQueryResult:
    """Збирає фокус дня та топ проблемних працівників.
    Builds the daily focus text and top employee problems.
    """

    dashboard_snapshot = load_dashboard_snapshot_from_path(database_path)
    employee_workspace = load_employee_workspace(database_path)
    problems: list[DailyFocusProblemRow] = []

    for row in employee_workspace.rows:
        if row.status_level == EmployeeStatusLevel.NORMAL:
            continue
        for problem in row.problems:
            problems.append(
                DailyFocusProblemRow(
                    employee_name=row.employee.full_name,
                    personnel_number=row.employee.personnel_number,
                    title=problem.title,
                    detail=problem.detail,
                )
            )
            if len(problems) >= limit:
                break
        if len(problems) >= limit:
            break

    return DailyFocusQueryResult(
        focus_text=dashboard_snapshot.focus_of_the_day,
        problems=tuple(problems),
    )
