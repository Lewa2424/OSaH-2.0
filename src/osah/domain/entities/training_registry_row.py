from dataclasses import dataclass

from osah.domain.entities.training_registry_filter import TrainingRegistryFilter


@dataclass(slots=True)
class TrainingRegistryRow:
    """Рядок реєстру інструктажів для UI.
    Строка реестра инструктажей для UI.
    """

    employee_personnel_number: str
    employee_full_name: str
    training_type_label: str
    event_date_label: str
    next_control_date_label: str
    status_label: str
    conducted_by_label: str
    row_filter: TrainingRegistryFilter
