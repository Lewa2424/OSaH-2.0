from dataclasses import dataclass

from osah.domain.entities.training_registry_filter import TrainingRegistryFilter
from osah.domain.entities.training_type import TrainingType


@dataclass(slots=True)
class TrainingWorkspaceRow:
    """Рядок Qt-реєстру інструктажів із причиною статусу.
    Qt training registry row with status reason.
    """

    record_id: int | None
    employee_personnel_number: str
    employee_full_name: str
    department_name: str
    site_name: str
    position_name: str
    training_type: TrainingType | None
    training_type_label: str
    event_date: str
    next_control_date: str
    status_filter: TrainingRegistryFilter
    status_label: str
    status_reason: str
    conducted_by: str
    note_text: str
    is_missing: bool
