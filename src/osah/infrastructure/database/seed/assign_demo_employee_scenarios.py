import random
from enum import StrEnum


class DemoEmployeeScenario(StrEnum):
    """Сценарій демо-наповнення для одного активного працівника.
    Demo seed scenario for one active employee.
    """

    OK = "ok"
    CRITICAL_TRAINING = "critical_training"
    CRITICAL_PPE = "critical_ppe"
    CRITICAL_MEDICAL = "critical_medical"
    CRITICAL_MISSING_TRAINING = "critical_missing_training"
    CRITICAL_PERMIT = "critical_permit"
    WARNING_TRAINING = "warning_training"
    WARNING_PPE = "warning_ppe"
    WARNING_MEDICAL = "warning_medical"
    WARNING_PERMIT = "warning_permit"
    MEDICAL_RESTRICTED = "medical_restricted"
    MISC_PERMIT = "misc_permit"


# ###### ПРИЗНАЧЕННЯ ДЕМО-СЦЕНАРІЇВ ПРАЦІВНИКАМ / ASSIGN DEMO EMPLOYEE SCENARIOS ######
def assign_demo_employee_scenarios(
    employee_rows: list[tuple[str, str, str, str, str]],
) -> dict[str, DemoEmployeeScenario]:
    """Розподіляє детерміновані сценарії між активними працівниками за квотами.
    Assigns deterministic scenarios to active employees using fixed quotas.
    """

    active_personnel_numbers = [row[0] for row in employee_rows if row[4] == "active"]
    shuffled_numbers = active_personnel_numbers.copy()
    random.Random(42).shuffle(shuffled_numbers)

    scenario_queue: list[DemoEmployeeScenario] = []
    scenario_queue.extend([DemoEmployeeScenario.CRITICAL_TRAINING] * 2)
    scenario_queue.extend([DemoEmployeeScenario.CRITICAL_PPE] * 2)
    scenario_queue.extend([DemoEmployeeScenario.CRITICAL_MEDICAL] * 2)
    scenario_queue.extend([DemoEmployeeScenario.CRITICAL_MISSING_TRAINING] * 2)
    scenario_queue.extend([DemoEmployeeScenario.CRITICAL_PERMIT] * 2)
    scenario_queue.extend([DemoEmployeeScenario.WARNING_TRAINING] * 3)
    scenario_queue.extend([DemoEmployeeScenario.WARNING_PPE] * 3)
    scenario_queue.extend([DemoEmployeeScenario.WARNING_MEDICAL] * 2)
    scenario_queue.extend([DemoEmployeeScenario.WARNING_PERMIT] * 2)
    scenario_queue.extend([DemoEmployeeScenario.MEDICAL_RESTRICTED] * 7)
    scenario_queue.extend([DemoEmployeeScenario.MISC_PERMIT] * 2)
    scenario_queue.extend([DemoEmployeeScenario.OK] * 19)

    if len(scenario_queue) != len(shuffled_numbers):
        raise ValueError(
            f"Demo scenario quota mismatch: {len(scenario_queue)} scenarios for {len(shuffled_numbers)} employees."
        )

    return dict(zip(shuffled_numbers, scenario_queue, strict=True))
