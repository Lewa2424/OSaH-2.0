from dataclasses import dataclass

from osah.domain.entities.employee import Employee
from osah.domain.entities.training_workspace_row import TrainingWorkspaceRow
from osah.domain.entities.training_workspace_summary import TrainingWorkspaceSummary


@dataclass(slots=True)
class TrainingWorkspace:
    """Повна модель даних Qt-модуля інструктажів.
    Complete data model for the Qt trainings module.
    """

    employees: tuple[Employee, ...]
    rows: tuple[TrainingWorkspaceRow, ...]
    summary: TrainingWorkspaceSummary
