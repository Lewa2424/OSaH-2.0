from datetime import datetime, timedelta

from osah.infrastructure.database.seed.assign_demo_employee_scenarios import (
    DemoEmployeeScenario,
    assign_demo_employee_scenarios,
)


# ###### ПОБУДОВА ДЕМО-НАРЯДІВ-ДОПУСКІВ / BUILD DEMO WORK PERMIT ROWS ######
def build_demo_work_permit_rows(
    employee_rows: list[tuple[str, str, str, str, str]],
    scenarios: dict[str, DemoEmployeeScenario] | None = None,
) -> tuple[list[tuple[str, str, str, str, str, str, str, str, str | None, str, str, str, str, str, str]], list[tuple[str, str, str]]]:
    """Повертає демонстраційні наряди-допуски та учасників за сценаріями працівників.
    Returns demo work permits and participants according to employee scenarios.
    """

    scenario_map = scenarios or assign_demo_employee_scenarios(employee_rows)
    now = datetime.now().replace(microsecond=0, second=0)
    permit_rows: list[tuple[str, str, str, str, str, str, str, str, str | None, str, str, str, str, str, str]] = []
    participant_rows: list[tuple[str, str, str]] = []

    critical_permit_employees = [
        personnel_number
        for personnel_number, scenario in scenario_map.items()
        if scenario == DemoEmployeeScenario.CRITICAL_PERMIT
    ]
    warning_permit_employees = [
        personnel_number
        for personnel_number, scenario in scenario_map.items()
        if scenario == DemoEmployeeScenario.WARNING_PERMIT
    ]
    misc_permit_employees = [
        personnel_number
        for personnel_number, scenario in scenario_map.items()
        if scenario == DemoEmployeeScenario.MISC_PERMIT
    ]

    if critical_permit_employees:
        starts_at = now - timedelta(hours=30)
        ends_at = now - timedelta(hours=2)
        permit_rows.append(_build_permit_row("ND-2026-CRIT", starts_at, ends_at, closed_at=None))
        for personnel_number in critical_permit_employees:
            participant_rows.append(("ND-2026-CRIT", personnel_number, "executor"))

    if warning_permit_employees:
        starts_at = now - timedelta(hours=8)
        ends_at = now + timedelta(hours=2)
        permit_rows.append(_build_permit_row("ND-2026-WARN", starts_at, ends_at, closed_at=None))
        for personnel_number in warning_permit_employees:
            participant_rows.append(("ND-2026-WARN", personnel_number, "executor"))

    if misc_permit_employees:
        starts_at = now - timedelta(hours=6)
        ends_at = now + timedelta(hours=2)
        permit_rows.append(_build_permit_row("ND-2026-MISC", starts_at, ends_at, closed_at=None))
        for personnel_number in misc_permit_employees:
            participant_rows.append(("ND-2026-MISC", personnel_number, "team_member"))

    closed_starts_at = now - timedelta(days=14)
    closed_ends_at = closed_starts_at + timedelta(hours=10)
    permit_rows.append(
        _build_permit_row(
            "ND-2026-DONE",
            closed_starts_at,
            closed_ends_at,
            closed_at=(closed_ends_at + timedelta(hours=1)).isoformat(sep=" "),
        )
    )
    ok_employees = [
        personnel_number
        for personnel_number, scenario in scenario_map.items()
        if scenario == DemoEmployeeScenario.OK
    ][:3]
    for personnel_number in ok_employees:
        participant_rows.append(("ND-2026-DONE", personnel_number, "observer"))

    return permit_rows, participant_rows


def _build_permit_row(
    permit_number: str,
    starts_at: datetime,
    ends_at: datetime,
    *,
    closed_at: str | None,
) -> tuple[str, str, str, str, str, str, str, str, str | None, str, str, str, str, str, str]:
    return (
        permit_number,
        "Контрольовані демонстраційні роботи",
        "Основний виробничий контур",
        starts_at.isoformat(sep=" "),
        ends_at.isoformat(sep=" "),
        "Іваненко Сергій Петрович",
        "Коваль Олена Вікторівна",
        "Демонстраційний наряд-допуск для типової ситуації.",
        closed_at,
        "done" if closed_at else "required_not_done",
        starts_at.date().isoformat() if closed_at else "",
        "Старший виробник робіт" if closed_at else "",
        "Відмітка про цільовий інструктаж у наряді." if closed_at else "",
        "Наряд-допуск підприємства",
        "",
    )
