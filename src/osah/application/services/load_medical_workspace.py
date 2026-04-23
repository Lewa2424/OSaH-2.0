from pathlib import Path

from osah.application.services.load_employee_registry import load_employee_registry
from osah.application.services.load_medical_registry import load_medical_registry
from osah.domain.entities.medical_workspace import MedicalWorkspace
from osah.domain.services.build_medical_workspace_rows import build_medical_workspace_rows
from osah.domain.services.build_medical_workspace_summary import build_medical_workspace_summary


# ###### ЗАВАНТАЖЕННЯ РОБОЧОГО ПРОСТОРУ МЕДИЦИНИ / LOAD MEDICAL WORKSPACE ######
def load_medical_workspace(database_path: Path) -> MedicalWorkspace:
    """Завантажує реальні дані для Qt-модуля медицини.
    Loads real data for the Qt medical module.
    """

    employees = load_employee_registry(database_path)
    rows = build_medical_workspace_rows(employees, load_medical_registry(database_path))
    return MedicalWorkspace(employees=employees, rows=rows, summary=build_medical_workspace_summary(rows))
