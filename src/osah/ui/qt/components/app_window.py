"""
AppWindow — головне вікно нового UI.
Збирає SideNav, TopCommandBar, StatusStrip і SectionContainer.
AppWindow — main window assembling all top level shell components.
"""
from PySide6.QtWidgets import QMainWindow, QSplitter, QVBoxLayout, QWidget
from PySide6.QtCore import Qt

from osah.application.services.application_context import ApplicationContext
from osah.application.services.load_dashboard_snapshot_from_path import load_dashboard_snapshot_from_path
from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.app_section import AppSection
from osah.ui.desktop.security.build_available_sections_for_role import build_available_sections_for_role
from osah.ui.qt.components.section_container import SectionContainer
from osah.ui.qt.components.side_nav import SideNav
from osah.ui.qt.components.status_strip import StatusStrip
from osah.ui.qt.components.top_command_bar import TopCommandBar
from osah.ui.qt.design.tokens import SIZE
from osah.ui.qt.screens.dashboard.dashboard_screen import DashboardScreen


class AppWindow(QMainWindow):
    """Головне вікно (Shell) застосунку.
    Main shell window managing the layout of panels and routing.
    """

    def __init__(self, app_context: ApplicationContext, access_role: AccessRole) -> None:
        super().__init__()
        self._app_context = app_context
        self._access_role = access_role

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
        # TODO: Завантажувати візуальний alert state
        dummy_levels = {}
        self._nav = SideNav(sections, access_role, dummy_levels)
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

        # Роутинг (поки що лише Dashboard)
        if section == AppSection.DASHBOARD:
            snapshot = load_dashboard_snapshot_from_path(self._app_context.database_path)
            screen = DashboardScreen(snapshot)
            layout.addWidget(screen)
        else:
            # Заглушка для неперенесених екранів
            from PySide6.QtWidgets import QLabel
            placeholder = QLabel(f"Екран '{section.value}' ще не мігрований на PySide6.")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(placeholder)
