from datetime import date, timedelta

from osah.infrastructure.database.seed.assign_demo_employee_scenarios import (
    DemoEmployeeScenario,
    assign_demo_employee_scenarios,
)

_BASE_PPE_ITEMS: tuple[str, ...] = (
    "Каска захисна",
    "Окуляри захисні",
    "Рукавиці комбіновані",
)


# ###### ПОБУДОВА ДЕМО-ЗАПИСІВ ЗІЗ / BUILD DEMO PPE ROWS ######
def build_demo_ppe_rows(
    employee_rows: list[tuple[str, str, str, str, str]],
    scenarios: dict[str, DemoEmployeeScenario] | None = None,
) -> list[tuple[str, str, int, int, str, str, int, str, str, str, str, str]]:
    """Повертає демонстраційні записи ЗІЗ з урахуванням сценаріїв працівників.
    Returns demo PPE records according to employee scenarios.
    """

    today = date.today()
    scenario_map = scenarios or assign_demo_employee_scenarios(employee_rows)
    rows: list[tuple[str, str, int, int, str, str, int, str, str, str, str, str]] = []

    for employee_row in employee_rows:
        if employee_row[4] != "active":
            continue
        personnel_number = employee_row[0]
        scenario = scenario_map[personnel_number]
        replacement_offset_days = 90
        is_issued = 1
        compliance_state = "checked"

        if scenario == DemoEmployeeScenario.CRITICAL_PPE:
            replacement_offset_days = -10
            is_issued = 0
            compliance_state = "legacy_not_tracked"
        elif scenario == DemoEmployeeScenario.WARNING_PPE:
            replacement_offset_days = 5

        for ppe_index, ppe_name in enumerate(_BASE_PPE_ITEMS):
            issue_date = today - timedelta(days=120 + ppe_index * 10)
            replacement_date = today + timedelta(days=replacement_offset_days)
            rows.append(
                (
                    personnel_number,
                    ppe_name,
                    1,
                    is_issued if ppe_index == 0 else 1,
                    issue_date.isoformat(),
                    replacement_date.isoformat(),
                    1,
                    "Норма видачі за посадою та виробничою дільницею.",
                    "required_not_issued" if is_issued == 0 and ppe_index == 0 else "issued",
                    compliance_state,
                    "Норма видачі СІЗ по підприємству",
                    "",
                )
            )

    return rows
