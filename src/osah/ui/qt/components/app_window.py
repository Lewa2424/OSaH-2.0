"""
Main Qt application shell window.
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QMainWindow, QSplitter, QVBoxLayout, QWidget

from osah.application.services.application_context import ApplicationContext
from osah.application.services.visual.load_visual_alert_state import load_visual_alert_state
from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.app_section import AppSection
from osah.ui.qt.components.section_container import SectionContainer
from osah.ui.qt.components.side_nav import SideNav
from osah.ui.qt.components.status_strip import StatusStrip
from osah.ui.qt.components.top_command_bar import TopCommandBar
from osah.ui.qt.design.tokens import SIZE
from osah.ui.qt.routing.build_screen_for_section import build_screen_for_section
from osah.ui.qt.routing.map_notification_source_to_problem_key import map_notification_source_to_problem_key
from osah.ui.qt.routing.qt_context import QtContext
from osah.ui.qt.routing.qt_navigation_intent import QtNavigationIntent
from osah.ui.shared.security.build_available_sections_for_role import build_available_sections_for_role


class AppWindow(QMainWindow):
    """Main shell window managing layout, routing and safe back navigation."""

    def __init__(self, app_context: ApplicationContext, access_role: AccessRole) -> None:
        super().__init__()
        self._app_context = app_context
        self._access_role = access_role
        self._current_section: AppSection | None = None
        self._current_navigation_intent: QtNavigationIntent | None = None
        self._navigation_history: list[tuple[AppSection, QtNavigationIntent | None]] = []

        self.setWindowTitle("OSaH 2.0")
        self.setMinimumSize(SIZE["window_min_w"], SIZE["window_min_h"])

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)

        sections = build_available_sections_for_role(access_role)
        visual_alert_state = load_visual_alert_state(self._app_context.database_path)

        self._nav = SideNav(sections, access_role, visual_alert_state.section_levels)
        self._nav.section_selected.connect(self._on_section_selected)
        splitter.addWidget(self._nav)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        self._top_bar = TopCommandBar(access_role)
        right_layout.addWidget(self._top_bar)

        self._content_container = SectionContainer()
        right_layout.addWidget(self._content_container)

        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        main_layout.addWidget(splitter)

        self._status_strip = StatusStrip(app_context.database_path, access_role)
        main_layout.addWidget(self._status_strip)

        self._install_navigation_shortcuts()
        self._navigate_to(AppSection.DASHBOARD, record_history=False)

    def _install_navigation_shortcuts(self) -> None:
        """###### ГАРЯЧІ КЛАВІШІ НАВІГАЦІЇ / NAVIGATION SHORTCUTS ######"""

        escape_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        escape_shortcut.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        escape_shortcut.activated.connect(self.navigate_back)

        alt_left_shortcut = QShortcut(QKeySequence("Alt+Left"), self)
        alt_left_shortcut.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        alt_left_shortcut.activated.connect(self.navigate_back)

    def _on_section_selected(self, section: AppSection) -> None:
        """###### ВИБІР РОЗДІЛУ / SECTION SELECT ######"""

        self._navigate_to(section)

    def _navigate_to(
        self,
        section: AppSection,
        *,
        intent: QtNavigationIntent | None = None,
        record_history: bool = True,
    ) -> None:
        """###### ПЕРЕХІД ДО РОЗДІЛУ / NAVIGATE TO SECTION ######"""

        effective_intent = intent
        if record_history and self._current_section is not None:
            current_state = (self._current_section, self._current_navigation_intent)
            next_state = (section, effective_intent)
            if current_state != next_state:
                self._navigation_history.append(current_state)

        self._nav.set_active_section(section)
        self._top_bar.set_section(section)

        layout = self._content_container.content_layout()
        while layout.count():
            item = layout.takeAt(0)
            if widget := item.widget():
                widget.deleteLater()

        context = QtContext(
            content_container=self._content_container,
            application_context=self._app_context,
            selected_section=section,
            access_role=self._access_role,
            navigation_intent=effective_intent,
        )
        self._current_section = section
        self._current_navigation_intent = effective_intent

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

    def navigate_back(self) -> None:
        """###### НАЗАД ПО ІСТОРІЇ / NAVIGATE BACK ######"""

        if not self._navigation_history:
            return
        section, intent = self._navigation_history.pop()
        self._navigate_to(section, intent=intent, record_history=False)

    def _open_employee_attention(self, personnel_number: str, source_module: str) -> None:
        """###### ПЕРЕХІД ДО ПРАЦІВНИКА / OPEN EMPLOYEE ATTENTION ######"""

        problem_key = map_notification_source_to_problem_key(source_module)
        intent = QtNavigationIntent(
            target_section=AppSection.EMPLOYEES,
            employee_personnel_number=personnel_number,
            problem_key=problem_key,
        )
        self._navigate_to(AppSection.EMPLOYEES, intent=intent)

    def _open_trainings_attention(self, status_filter: str) -> None:
        """###### ПЕРЕХІД ДО ІНСТРУКТАЖІВ / OPEN TRAININGS ATTENTION ######"""

        intent = QtNavigationIntent(
            target_section=AppSection.TRAININGS,
            training_status_filter=status_filter,
        )
        self._navigate_to(AppSection.TRAININGS, intent=intent)

    def _open_ppe_attention(self, status_filter: str) -> None:
        """###### ПЕРЕХІД ДО ЗІЗ / OPEN PPE ATTENTION ######"""

        intent = QtNavigationIntent(
            target_section=AppSection.PPE,
            ppe_status_filter=status_filter,
        )
        self._navigate_to(AppSection.PPE, intent=intent)

    def _open_medical_attention(self, status_filter: str) -> None:
        """###### ПЕРЕХІД ДО МЕДИЦИНИ / OPEN MEDICAL ATTENTION ######"""

        intent = QtNavigationIntent(
            target_section=AppSection.MEDICAL,
            medical_status_filter=status_filter,
        )
        self._navigate_to(AppSection.MEDICAL, intent=intent)

    def _open_work_permits_attention(self, status_filter: str) -> None:
        """###### ПЕРЕХІД ДО НАРЯДІВ / OPEN WORK PERMITS ATTENTION ######"""

        intent = QtNavigationIntent(
            target_section=AppSection.WORK_PERMITS,
            work_permit_status_filter=status_filter,
        )
        self._navigate_to(AppSection.WORK_PERMITS, intent=intent)


def _notification_source_for_section(section: AppSection) -> str:
    """###### ДЖЕРЕЛО СПОВІЩЕННЯ СЕКЦІЇ / SECTION NOTIFICATION SOURCE ######"""

    if section == AppSection.TRAININGS:
        return "trainings.registry"
    if section == AppSection.PPE:
        return "ppe.registry"
    if section == AppSection.MEDICAL:
        return "medical.registry"
    if section == AppSection.WORK_PERMITS:
        return "work_permits.registry"
    return "employees.registry"
