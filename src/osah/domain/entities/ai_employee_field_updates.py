from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class AiEmployeeFieldUpdates:
    """Зміни полів картки працівника для AI-команди.
    Employee card field updates for an AI command.
    """

    position_name: str | None = None
    department_name: str | None = None
    employment_status: str | None = None
