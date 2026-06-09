from datetime import date, timedelta

from osah.infrastructure.database.seed.assign_demo_employee_scenarios import (
    DemoEmployeeScenario,
    assign_demo_employee_scenarios,
)


# ###### ПОБУДОВА ДЕМО-ЗАПИСІВ МЕДИЦИНИ / BUILD DEMO MEDICAL ROWS ######
def build_demo_medical_rows(
    employee_rows: list[tuple[str, str, str, str, str]],
    scenarios: dict[str, DemoEmployeeScenario] | None = None,
) -> list[tuple[str, str, str, str, str, str, str, str]]:
    """Повертає демонстраційні медзаписи з урахуванням сценаріїв працівників.
    Returns demo medical records according to employee scenarios.
    """

    today = date.today()
    scenario_map = scenarios or assign_demo_employee_scenarios(employee_rows)
    rows: list[tuple[str, str, str, str, str, str, str, str]] = []

    for employee_row in employee_rows:
        if employee_row[4] != "active":
            continue
        personnel_number = employee_row[0]
        scenario = scenario_map[personnel_number]
        valid_from = today - timedelta(days=180)
        valid_until = today + timedelta(days=90)
        medical_decision = "fit"
        restriction_note = ""

        if scenario == DemoEmployeeScenario.CRITICAL_MEDICAL:
            valid_until = today - timedelta(days=10)
            medical_decision = "not_fit"
            restriction_note = "Тимчасово відсторонений до повторного медогляду."
        elif scenario == DemoEmployeeScenario.MEDICAL_RESTRICTED:
            medical_decision = "restricted"
            restriction_note = "Без робіт на висоті та без нічних змін."
        elif scenario == DemoEmployeeScenario.WARNING_MEDICAL:
            valid_until = today + timedelta(days=5)

        rows.append(
            (
                personnel_number,
                valid_from.isoformat(),
                valid_until.isoformat(),
                medical_decision,
                restriction_note,
                "harmful_or_dangerous_factors",
                "Направлення на обов'язковий медогляд",
                "",
            )
        )

    return rows
