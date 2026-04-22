from dataclasses import dataclass

from osah.domain.entities.employee import Employee
from osah.domain.entities.ppe_workspace_row import PpeWorkspaceRow
from osah.domain.entities.ppe_workspace_summary import PpeWorkspaceSummary


@dataclass(slots=True)
class PpeWorkspace:
    """Повна модель даних Qt-модуля ЗІЗ.
    Complete data model for the Qt PPE module.
    """

    employees: tuple[Employee, ...]
    rows: tuple[PpeWorkspaceRow, ...]
    summary: PpeWorkspaceSummary
