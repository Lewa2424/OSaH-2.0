"""
build_screen_for_section — фабрика для маршутизації екранів.
Повертає відповідний екран для вибраного розділу.
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QWidget

from osah.application.services.load_dashboard_snapshot_from_path import load_dashboard_snapshot_from_path
from osah.domain.entities.app_section import AppSection
from osah.ui.qt.routing.qt_context import QtContext
from osah.ui.qt.screens.dashboard.dashboard_screen import DashboardScreen


def build_screen_for_section(context: QtContext) -> QWidget:
    """Будує та повертає віджет екрану для поточного розділу.
    Builds and returns the screen widget for the current section.
    """
    
    if context.selected_section == AppSection.DASHBOARD:
        snapshot = load_dashboard_snapshot_from_path(context.application_context.database_path)
        return DashboardScreen(snapshot)

    # Заглушка для неперенесених екранів
    placeholder = QLabel(f"Екран '{context.selected_section.value}' ще не мігрований на PySide6.")
    placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
    placeholder.setProperty("role", "status_muted")
    return placeholder
