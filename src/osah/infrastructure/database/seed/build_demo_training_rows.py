from datetime import date, timedelta

from osah.infrastructure.database.seed.assign_demo_employee_scenarios import (
    DemoEmployeeScenario,
    assign_demo_employee_scenarios,
)


# ###### ПОБУДОВА ДЕМО-ЗАПИСІВ ІНСТРУКТАЖІВ / BUILD DEMO TRAINING ROWS ######
def build_demo_training_rows(
    employee_rows: list[tuple[str, str, str, str, str]],
    scenarios: dict[str, DemoEmployeeScenario] | None = None,
) -> list[tuple[str, str, str, str, str, str, str, int, str, str, str, str, str, str, str]]:
    """Повертає демонстраційні записи інструктажів з урахуванням сценаріїв працівників.
    Returns demo training records according to employee scenarios.
    """

    today = date.today()
    scenario_map = scenarios or assign_demo_employee_scenarios(employee_rows)
    rows: list[tuple[str, str, str, str, str, str, str, int, str, str, str, str, str, str, str]] = []

    for employee_row in employee_rows:
        if employee_row[4] != "active":
            continue
        personnel_number = employee_row[0]
        scenario = scenario_map[personnel_number]
        if scenario == DemoEmployeeScenario.CRITICAL_MISSING_TRAINING:
            continue

        introductory_event_date = today - timedelta(days=320)
        introductory_next_control = today + timedelta(days=120)
        rows.append(
            _build_training_row(
                personnel_number,
                "introductory",
                introductory_event_date,
                introductory_next_control,
                next_control_basis="requires_primary_after_introductory",
                knowledge_check_result="satisfactory",
                work_admission_status="allowed",
                knowledge_check_note="Вступний інструктаж проведено.",
                note_text="Вступний інструктаж на підприємстві.",
            )
        )

        primary_event_date = today - timedelta(days=280)
        primary_next_control = today + timedelta(days=120)
        rows.append(
            _build_training_row(
                personnel_number,
                "primary",
                primary_event_date,
                primary_next_control,
                knowledge_check_result="satisfactory",
                work_admission_status="allowed",
                knowledge_check_note="Первинний інструктаж проведено відповідальною особою.",
                note_text="Базовий допуск до роботи на робочому місці.",
            )
        )

        if scenario not in {
            DemoEmployeeScenario.CRITICAL_TRAINING,
            DemoEmployeeScenario.WARNING_TRAINING,
        }:
            continue

        repeated_event_date = today - timedelta(days=120)
        repeated_next_control = today + timedelta(days=90)
        knowledge_check_result = "satisfactory"
        work_admission_status = "allowed"
        knowledge_check_note = "Перевірку знань проведено відповідальною особою."

        if scenario == DemoEmployeeScenario.CRITICAL_TRAINING:
            knowledge_check_result = "unsatisfactory"
            work_admission_status = "not_allowed"
            knowledge_check_note = "Цільовий інструктаж завершено з незадовільним результатом."
        elif scenario == DemoEmployeeScenario.WARNING_TRAINING:
            repeated_next_control = today + timedelta(days=5)

        rows.append(
            _build_training_row(
                personnel_number,
                "repeated",
                repeated_event_date,
                repeated_next_control,
                knowledge_check_result=knowledge_check_result,
                work_admission_status=work_admission_status,
                knowledge_check_note=knowledge_check_note,
                note_text="Плановий контроль знань з охорони праці.",
            )
        )

    return rows


def _build_training_row(
    personnel_number: str,
    training_type: str,
    event_date: date,
    next_control_date: date,
    *,
    knowledge_check_result: str,
    work_admission_status: str,
    knowledge_check_note: str,
    note_text: str,
    next_control_basis: str = "manual",
) -> tuple[str, str, str, str, str, str, str, int, str, str, str, str, str, str, str]:
    return (
        personnel_number,
        training_type,
        event_date.isoformat(),
        next_control_date.isoformat(),
        "Коваль Олена Вікторівна",
        note_text,
        "own_employee",
        1,
        "regular",
        next_control_basis,
        knowledge_check_result,
        work_admission_status,
        knowledge_check_note,
        "Журнал інструктажів підприємства",
        "",
    )
