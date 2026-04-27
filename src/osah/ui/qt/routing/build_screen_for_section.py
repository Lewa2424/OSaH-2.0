"""
Screen factory for Qt section routing.
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QWidget

from osah.application.services.load_about_snapshot import load_about_snapshot
from osah.application.services.load_audit_log_entries import load_audit_log_entries
from osah.application.services.load_dashboard_snapshot_from_path import load_dashboard_snapshot_from_path
from osah.application.services.load_employee_workspace import load_employee_workspace
from osah.application.services.load_medical_workspace import load_medical_workspace
from osah.application.services.load_ppe_workspace import load_ppe_workspace
from osah.application.services.load_training_workspace import load_training_workspace
from osah.application.services.load_work_permit_workspace import load_work_permit_workspace
from osah.domain.entities.app_section import AppSection
from osah.ui.qt.routing.qt_context import QtContext
from osah.ui.qt.screens.about.about_screen import AboutScreen
from osah.ui.qt.screens.archive.archive_screen import ArchiveScreen
from osah.ui.qt.screens.contractors.contractors_screen import ContractorsScreen
from osah.ui.qt.screens.dashboard.dashboard_screen import DashboardScreen
from osah.ui.qt.screens.employees.employees_screen import EmployeesScreen
from osah.ui.qt.screens.medical.medical_screen import MedicalScreen
from osah.ui.qt.screens.news.news_screen import NewsScreen
from osah.ui.qt.screens.ppe.ppe_screen import PpeScreen
from osah.ui.qt.screens.reports.reports_screen import ReportsScreen
from osah.ui.qt.screens.settings.settings_screen import SettingsScreen
from osah.ui.qt.screens.trainings.trainings_screen import TrainingsScreen
from osah.ui.qt.screens.work_permits.work_permits_screen import WorkPermitsScreen


# ###### ПОБУДОВА ЕКРАНУ РОЗДІЛУ / BUILD SECTION SCREEN ######
def build_screen_for_section(context: QtContext) -> QWidget:
    """Builds and returns screen widget for selected app section."""

    if context.selected_section == AppSection.DASHBOARD:
        snapshot = load_dashboard_snapshot_from_path(context.application_context.database_path)
        audit_entries = load_audit_log_entries(context.application_context.database_path, limit=80)
        return DashboardScreen(snapshot, audit_entries)

    if context.selected_section == AppSection.EMPLOYEES:
        workspace = load_employee_workspace(context.application_context.database_path)
        intent = context.navigation_intent
        return EmployeesScreen(
            context.application_context.database_path,
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
            initial_personnel_number=intent.employee_personnel_number if intent else None,
        )

    if context.selected_section == AppSection.PPE:
        intent = context.navigation_intent
        return PpeScreen(
            context.application_context.database_path,
            load_ppe_workspace(context.application_context.database_path),
            initial_status=intent.ppe_status_filter if intent else None,
            initial_personnel_number=intent.employee_personnel_number if intent else None,
        )

    if context.selected_section == AppSection.MEDICAL:
        intent = context.navigation_intent
        return MedicalScreen(
            context.application_context.database_path,
            load_medical_workspace(context.application_context.database_path),
            initial_status=intent.medical_status_filter if intent else None,
            initial_personnel_number=intent.employee_personnel_number if intent else None,
        )

    if context.selected_section == AppSection.WORK_PERMITS:
        intent = context.navigation_intent
        return WorkPermitsScreen(
            context.application_context.database_path,
            load_work_permit_workspace(context.application_context.database_path),
            initial_status=intent.work_permit_status_filter if intent else None,
            initial_personnel_number=intent.employee_personnel_number if intent else None,
        )

    if context.selected_section == AppSection.REPORTS:
        return ReportsScreen(context.application_context.database_path)

    if context.selected_section == AppSection.NEWS_NPA:
        return NewsScreen(context.application_context.database_path)

    if context.selected_section == AppSection.SETTINGS:
        return SettingsScreen(context.application_context.database_path, context.access_role)

    if context.selected_section == AppSection.ARCHIVE:
        return ArchiveScreen(context.application_context.database_path, context.access_role)

    if context.selected_section == AppSection.CONTRACTORS:
        return ContractorsScreen(context.application_context.database_path, context.access_role)

    if context.selected_section == AppSection.ABOUT:
        return AboutScreen(
            load_about_snapshot(
                context.application_context.database_path,
                context.application_context.log_path,
            )
        )

    placeholder = QLabel(f"Екран '{context.selected_section.value}' ще не мігрований на PySide6.")
    placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
    placeholder.setProperty("role", "status_muted")
    return placeholder
