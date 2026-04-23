from dataclasses import dataclass

from osah.domain.entities.employee import Employee
from osah.domain.entities.work_permit_workspace_row import WorkPermitWorkspaceRow
from osah.domain.entities.work_permit_workspace_summary import WorkPermitWorkspaceSummary


@dataclass(slots=True)
class WorkPermitWorkspace:
    """Робоча модель Qt-модуля нарядів-допусків.
    Workspace model for the Qt work permits module.
    """

    employees: tuple[Employee, ...]
    rows: tuple[WorkPermitWorkspaceRow, ...]
    summary: WorkPermitWorkspaceSummary
