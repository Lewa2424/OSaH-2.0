"""
build_screen_for_section — фабрика для маршутизації екранів.
Повертає відповідний екран для вибраного розділу.
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QWidget

from osah.application.services.load_dashboard_snapshot_from_path import load_dashboard_snapshot_from_path
from osah.application.services.load_employee_workspace import load_employee_workspace
from osah.application.services.load_ppe_workspace import load_ppe_workspace
from osah.application.services.load_training_workspace import load_training_workspace
from osah.domain.entities.app_section import AppSection
from osah.ui.qt.routing.qt_context import QtContext
from osah.ui.qt.screens.dashboard.dashboard_screen import DashboardScreen
from osah.ui.qt.screens.employees.employees_screen import EmployeesScreen
from osah.ui.qt.screens.ppe.ppe_screen import PpeScreen
from osah.ui.qt.screens.trainings.trainings_screen import TrainingsScreen


def build_screen_for_section(context: QtContext) -> QWidget:
    """Будує та повертає віджет екрану для поточного розділу.
    Builds and returns the screen widget for the current section.
    """
    
    if context.selected_section == AppSection.DASHBOARD:
        snapshot = load_dashboard_snapshot_from_path(context.application_context.database_path)
        return DashboardScreen(snapshot)

    if context.selected_section == AppSection.EMPLOYEES:
        workspace = load_employee_workspace(context.application_context.database_path)
        intent = context.navigation_intent
        return EmployeesScreen(
            workspace,
            initial_personnel_number=intent.employee_personnel_number if intent else None,
            initial_problem_key=intent.problem_key if intent else None,
        )

    if context.selected_section == AppSection.TRAININGS:
        intent = context.navigation_intent
        return TrainingsScreen(
            context.application_context.database_path,
            load_training_workspace(context.application_context.database_path),
            initial_status=intent.training_status_filter if intent else None,
        )

    if context.selected_section == AppSection.PPE:
        intent = context.navigation_intent
        return PpeScreen(
            context.application_context.database_path,
            load_ppe_workspace(context.application_context.database_path),
            initial_status=intent.ppe_status_filter if intent else None,
        )

    # Заглушка для неперенесених екранів
    placeholder = QLabel(f"Екран '{context.selected_section.value}' ще не мігрований на PySide6.")
    placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
    placeholder.setProperty("role", "status_muted")
    return placeholder
