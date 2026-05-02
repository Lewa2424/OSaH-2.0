from dataclasses import dataclass


@dataclass(slots=True)
class Employee:
    """Базова сутність працівника.
    Базовая сущность сотрудника.
    """

    personnel_number: str
    full_name: str
    position_name: str
    department_name: str
    employment_status: str
    photo_path: str | None = None
    created_at_text: str = ""
