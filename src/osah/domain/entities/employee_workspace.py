from dataclasses import dataclass

from osah.domain.entities.employee_workspace_row import EmployeeWorkspaceRow


@dataclass(slots=True)
class EmployeeWorkspace:
    """Повна модель даних екрана працівників.
    Complete data model for the employees screen.
    """

    enterprise_name: str
    rows: tuple[EmployeeWorkspaceRow, ...]
