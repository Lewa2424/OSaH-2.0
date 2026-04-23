"""
AppWindow — головне вікно нового UI.
Збирає SideNav, TopCommandBar, StatusStrip і SectionContainer.
AppWindow — main window assembling all top level shell components.
"""
from PySide6.QtWidgets import QMainWindow, QSplitter, QVBoxLayout, QWidget
from PySide6.QtCore import Qt

from osah.application.services.application_context import ApplicationContext
from osah.application.services.load_dashboard_snapshot_from_path import load_dashboard_snapshot_from_path
from osah.application.services.visual.load_visual_alert_state import load_visual_alert_state
from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.app_section import AppSection
from osah.ui.shared.security.build_available_sections_for_role import build_available_sections_for_role
from osah.ui.qt.components.section_container import SectionContainer
from osah.ui.qt.components.side_nav import SideNav
from osah.ui.qt.components.status_strip import StatusStrip
from osah.ui.qt.components.top_command_bar import TopCommandBar
from osah.ui.qt.design.tokens import SIZE
from osah.ui.qt.routing.map_notification_source_to_problem_key import map_notification_source_to_problem_key
from osah.ui.qt.routing.qt_context import QtContext
from osah.ui.qt.routing.qt_navigation_intent import QtNavigationIntent
from osah.ui.qt.routing.build_screen_for_section import build_screen_for_section


class AppWindow(QMainWindow):
    """Головне вікно (Shell) застосунку.
    Main shell window managing the layout of panels and routing.
    """

    def __init__(self, app_context: ApplicationContext, access_role: AccessRole) -> None:
        super().__init__()
        self._app_context = app_context
        self._access_role = access_role
        self._pending_navigation_intent: QtNavigationIntent | None = None

        self.setWindowTitle("OSaH 2.0")
        self.setMinimumSize(SIZE["window_min_w"], SIZE["window_min_h"])

        # Збираємо скелет / Assemble skeleton
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # QSplitter для [Навігація | Контент]
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)

        # 1. Ліва панель / Side Nav
        sections = build_available_sections_for_role(access_role)
        visual_alert_state = load_visual_alert_state(self._app_context.database_path)
        
        self._nav = SideNav(sections, access_role, visual_alert_state.section_levels)
        self._nav.section_selected.connect(self._on_section_selected)
        splitter.addWidget(self._nav)

        # 2. Права частина (Верхня панель + Контент)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        self._top_bar = TopCommandBar(access_role)
        right_layout.addWidget(self._top_bar)

        self._content_container = SectionContainer()
        right_layout.addWidget(self._content_container)

        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 0) # Nav фіксована
        splitter.setStretchFactor(1, 1) # Контент розтягується

        main_layout.addWidget(splitter)

        # 3. Нижня смужка / Status Strip
        self._status_strip = StatusStrip(app_context.database_path, access_role)
        main_layout.addWidget(self._status_strip)

        # Стартовий екран
        self._on_section_selected(AppSection.DASHBOARD)

    def _on_section_selected(self, section: AppSection) -> None:
        """Перемикає вміст центральної області."""
        self._nav.set_active_section(section)
        self._top_bar.set_section(section)

        # Очищення старого (швидкий спосіб)
        layout = self._content_container.content_layout()
        while layout.count():
            item = layout.takeAt(0)
            if widget := item.widget():
                widget.deleteLater()

        # Роутинг / Routing
        context = QtContext(
            content_container=self._content_container,
            application_context=self._app_context,
            selected_section=section,
            access_role=self._access_role,
            navigation_intent=self._pending_navigation_intent,
        )
        self._pending_navigation_intent = None
        screen = build_screen_for_section(context)
        if hasattr(screen, "employee_attention_requested"):
            screen.employee_attention_requested.connect(self._open_employee_attention)
        if hasattr(screen, "trainings_attention_requested"):
            screen.trainings_attention_requested.connect(self._open_trainings_attention)
        if hasattr(screen, "ppe_attention_requested"):
            screen.ppe_attention_requested.connect(self._open_ppe_attention)
        if hasattr(screen, "medical_attention_requested"):
            screen.medical_attention_requested.connect(self._open_medical_attention)
        if hasattr(screen, "work_permits_attention_requested"):
            screen.work_permits_attention_requested.connect(self._open_work_permits_attention)
        if hasattr(screen, "employee_open_requested"):
            screen.employee_open_requested.connect(
                lambda personnel_number, source=section: self._open_employee_attention(
                    personnel_number,
                    _notification_source_for_section(source),
                )
            )
        
        from osah.ui.qt.components.animations.fade_in import apply_fade_in
        apply_fade_in(screen)
        
        layout.addWidget(screen)

    # ###### ВІДКРИТТЯ ПРАЦІВНИКА ЗІ СПОВІЩЕННЯ / OPEN EMPLOYEE FROM ALERT ######
    def _open_employee_attention(self, personnel_number: str, source_module: str) -> None:
        """Переходить із Dashboard до картки працівника за сигналом проблеми.
        Navigates from Dashboard to an employee card from a problem signal.
        """

        problem_key = map_notification_source_to_problem_key(source_module)
        self._pending_navigation_intent = QtNavigationIntent(
            target_section=AppSection.EMPLOYEES,
            employee_personnel_number=personnel_number,
            problem_key=problem_key,
        )
        self._on_section_selected(AppSection.EMPLOYEES)

    # ###### ВІДКРИТТЯ ПРОБЛЕМНИХ ІНСТРУКТАЖІВ / OPEN TRAINING ALERTS ######
    def _open_trainings_attention(self, status_filter: str) -> None:
        """Переходить із Dashboard до відфільтрованого модуля інструктажів.
        Navigates from Dashboard to filtered trainings module.
        """

        self._pending_navigation_intent = QtNavigationIntent(
            target_section=AppSection.TRAININGS,
            training_status_filter=status_filter,
        )
        self._on_section_selected(AppSection.TRAININGS)

    # ###### ВІДКРИТТЯ ПРОБЛЕМНИХ ЗІЗ / OPEN PPE ALERTS ######
    def _open_ppe_attention(self, status_filter: str) -> None:
        """Переходить із Dashboard до відфільтрованого модуля ЗІЗ.
        Navigates from Dashboard to filtered PPE module.
        """

        self._pending_navigation_intent = QtNavigationIntent(
            target_section=AppSection.PPE,
            ppe_status_filter=status_filter,
        )
        self._on_section_selected(AppSection.PPE)

    # ###### ВІДКРИТТЯ ПРОБЛЕМНОЇ МЕДИЦИНИ / OPEN MEDICAL ALERTS ######
    def _open_medical_attention(self, status_filter: str) -> None:
        """Переходить із Dashboard до відфільтрованого модуля медицини.
        Navigates from Dashboard to filtered medical module.
        """

        self._pending_navigation_intent = QtNavigationIntent(
            target_section=AppSection.MEDICAL,
            medical_status_filter=status_filter,
        )
        self._on_section_selected(AppSection.MEDICAL)

    # ###### ВІДКРИТТЯ ПРОБЛЕМНИХ НАРЯДІВ / OPEN WORK PERMIT ALERTS ######
    def _open_work_permits_attention(self, status_filter: str) -> None:
        """Переходить із Dashboard до відфільтрованого модуля нарядів-допусків.
        Navigates from Dashboard to filtered work permits module.
        """

        self._pending_navigation_intent = QtNavigationIntent(
            target_section=AppSection.WORK_PERMITS,
            work_permit_status_filter=status_filter,
        )
        self._on_section_selected(AppSection.WORK_PERMITS)


# ###### ДЖЕРЕЛО СПОВІЩЕННЯ СЕКЦІЇ / SECTION NOTIFICATION SOURCE ######
def _notification_source_for_section(section: AppSection) -> str:
    """Повертає source_module для переходу з профільного модуля до картки працівника.
    Returns source_module for navigation from a domain module to an employee card.
    """

    if section == AppSection.TRAININGS:
        return "trainings.registry"
    if section == AppSection.PPE:
        return "ppe.registry"
    if section == AppSection.MEDICAL:
        return "medical.registry"
    if section == AppSection.WORK_PERMITS:
        return "work_permits.registry"
    return "employees.registry"
