from pathlib import Path

from osah.application.services.load_employee_registry import load_employee_registry
from osah.application.services.load_training_registry import load_training_registry
from osah.domain.entities.training_workspace import TrainingWorkspace
from osah.domain.services.build_training_workspace_rows import build_training_workspace_rows
from osah.domain.services.build_training_workspace_summary import build_training_workspace_summary


# ###### ЗАВАНТАЖЕННЯ РОБОЧОГО ПРОСТОРУ ІНСТРУКТАЖІВ / LOAD TRAINING WORKSPACE ######
def load_training_workspace(database_path: Path) -> TrainingWorkspace:
    """Завантажує реальні дані для Qt-модуля інструктажів.
    Loads real data for the Qt trainings module.
    """

    employees = load_employee_registry(database_path)
    rows = build_training_workspace_rows(employees, load_training_registry(database_path))
    return TrainingWorkspace(
        employees=employees,
        rows=rows,
        summary=build_training_workspace_summary(rows),
    )
