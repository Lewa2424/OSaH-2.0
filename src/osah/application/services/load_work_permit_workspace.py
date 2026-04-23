from pathlib import Path

from osah.application.services.load_employee_registry import load_employee_registry
from osah.application.services.load_employee_workspace import load_employee_workspace
from osah.application.services.load_work_permit_registry import load_work_permit_registry
from osah.domain.entities.work_permit_workspace import WorkPermitWorkspace
from osah.domain.services.build_work_permit_workspace_rows import build_work_permit_workspace_rows
from osah.domain.services.build_work_permit_workspace_summary import build_work_permit_workspace_summary


# ###### ЗАВАНТАЖЕННЯ РОБОЧОГО ПРОСТОРУ НАРЯДІВ / LOAD WORK PERMIT WORKSPACE ######
def load_work_permit_workspace(database_path: Path) -> WorkPermitWorkspace:
    """Завантажує реальні дані для Qt-модуля нарядів-допусків.
    Loads real data for the Qt work permits module.
    """

    employee_workspace = load_employee_workspace(database_path)
    rows = build_work_permit_workspace_rows(load_work_permit_registry(database_path), employee_workspace.rows)
    return WorkPermitWorkspace(
        employees=load_employee_registry(database_path),
        rows=rows,
        summary=build_work_permit_workspace_summary(rows),
    )
