from pathlib import Path

from osah.application.services.load_employee_registry import load_employee_registry
from osah.application.services.load_ppe_registry import load_ppe_registry
from osah.domain.entities.ppe_workspace import PpeWorkspace
from osah.domain.services.build_ppe_workspace_rows import build_ppe_workspace_rows
from osah.domain.services.build_ppe_workspace_summary import build_ppe_workspace_summary


# ###### ЗАВАНТАЖЕННЯ РОБОЧОГО ПРОСТОРУ ЗІЗ / LOAD PPE WORKSPACE ######
def load_ppe_workspace(database_path: Path) -> PpeWorkspace:
    """Завантажує реальні дані для Qt-модуля ЗІЗ.
    Loads real data for the Qt PPE module.
    """

    employees = load_employee_registry(database_path)
    rows = build_ppe_workspace_rows(employees, load_ppe_registry(database_path))
    return PpeWorkspace(employees=employees, rows=rows, summary=build_ppe_workspace_summary(rows))
