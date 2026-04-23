from dataclasses import dataclass

from osah.domain.entities.employee import Employee
from osah.domain.entities.medical_workspace_row import MedicalWorkspaceRow
from osah.domain.entities.medical_workspace_summary import MedicalWorkspaceSummary


@dataclass(slots=True)
class MedicalWorkspace:
    """Повна модель даних Qt-модуля медицини.
    Complete data model for the Qt medical module.
    """

    employees: tuple[Employee, ...]
    rows: tuple[MedicalWorkspaceRow, ...]
    summary: MedicalWorkspaceSummary
