from dataclasses import dataclass


@dataclass(slots=True)
class AiEntityChoice:
    """Варіант сутності для уточнення AI-команди.
    Entity option shown when an AI command is ambiguous.
    """

    choice_id: str
    label: str
    personnel_number: str | None = None
    choice_kind: str = "employee"
