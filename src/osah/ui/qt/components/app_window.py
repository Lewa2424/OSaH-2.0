"""
Main Qt application shell window.
"""

from datetime import datetime, timedelta

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QComboBox, QLineEdit, QMainWindow, QSplitter, QTextEdit, QVBoxLayout, QWidget

from osah.application.services.application_context import ApplicationContext
from osah.application.services.load_manual_report_settings import load_manual_report_settings
from osah.application.services.save_manual_report_settings import save_manual_report_settings
from osah.application.services.load_system_settings_workspace import load_system_settings_workspace
from osah.application.services.visual.load_visual_alert_state import load_visual_alert_state
from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.app_section import AppSection
from osah.domain.entities.manual_report_settings import ManualReportSettings
from osah.domain.services.should_prompt_manual_report import should_prompt_manual_report
from osah.ui.qt.branding import DISPLAY_NAME
from osah.ui.qt.components.section_container import SectionContainer
from osah.ui.qt.components.show_manual_report_prompt_dialog import show_manual_report_prompt_dialog
from osah.ui.qt.components.side_nav import SideNav
from osah.ui.qt.components.status_strip import StatusStrip
from osah.ui.qt.components.top_command_bar import TopCommandBar
from osah.ui.qt.design.tokens import SIZE
from osah.ui.qt.routing.build_screen_for_section import build_screen_for_section
from osah.ui.qt.routing.map_notification_source_to_problem_key import map_notification_source_to_problem_key
from osah.ui.qt.routing.qt_context import QtContext
from osah.ui.qt.routing.qt_navigation_intent import QtNavigationIntent
from osah.ui.qt.services.save_manual_report_via_dialog import save_manual_report_via_dialog
from osah.ui.shared.security.build_available_sections_for_role import build_available_sections_for_role
from osah.ui.qt.workers.news_refresh_worker import NewsRefreshWorker
from osah.ui.qt.workers.worker_task_controller import WorkerTaskController


class AppWindow(QMainWindow):
    """Main shell window managing layout, routing and safe back navigation."""

    def __init__(self, app_context: ApplicationContext, access_role: AccessRole) -> None:
        super().__init__()
        self._app_context = app_context
        self._access_role = access_role
        self._current_section: AppSection | None = None
        self._current_navigation_intent: QtNavigationIntent | None = None
        self._navigation_history: list[tuple[AppSection, QtNavigationIntent | None]] = []

        self.setWindowTitle(DISPLAY_NAME)
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
        self._news_task_controller = WorkerTaskController()
        self._news_task_controller.success.connect(self._on_news_refresh_completed)
        self._news_task_controller.error.connect(self._on_news_refresh_failed)
        self._news_timer = QTimer(self)
        self._news_timer.setSingleShot(True)
        self._news_timer.timeout.connect(self._run_scheduled_news_refresh)
        self._manual_report_prompt_open = False
        self._last_time_sync_marker = self._build_time_sync_marker()
        self._last_day_sync_marker = self._build_day_sync_marker()
        self._install_time_tracking()
        self._schedule_news_refresh()
        self._install_manual_report_reminder()

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

        allowed_sections = build_available_sections_for_role(self._access_role)
        if section not in allowed_sections:
            return

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
        if hasattr(screen, "news_refresh_schedule_saved"):
            screen.news_refresh_schedule_saved.connect(self._on_news_refresh_schedule_saved)
        if hasattr(screen, "module_navigation_requested"):
            screen.module_navigation_requested.connect(self._open_module_for_employee)
        if hasattr(screen, "module_record_navigation_requested"):
            screen.module_record_navigation_requested.connect(self._open_module_record_for_employee)
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

    def _open_module_for_employee(self, target_section: AppSection, personnel_number: str) -> None:
        """###### ПЕРЕХІД ДО МОДУЛЯ ДЛЯ ПРАЦІВНИКА / OPEN MODULE FOR EMPLOYEE ######"""

        intent = QtNavigationIntent(
            target_section=target_section,
            employee_personnel_number=personnel_number,
        )
        self._navigate_to(target_section, intent=intent)

    def _open_module_record_for_employee(
        self,
        target_section: AppSection,
        personnel_number: str,
        record_id: int,
    ) -> None:
        """Відкриває конкретний запис модуля для працівника.
        Opens a concrete module record for the selected employee.
        """

        intent = QtNavigationIntent(
            target_section=target_section,
            employee_personnel_number=personnel_number,
            training_record_id=record_id if target_section == AppSection.TRAININGS and record_id > 0 else None,
            ppe_record_id=record_id if target_section == AppSection.PPE and record_id > 0 else None,
            medical_record_id=record_id if target_section == AppSection.MEDICAL and record_id > 0 else None,
            work_permit_record_id=record_id if target_section == AppSection.WORK_PERMITS and record_id > 0 else None,
        )
        self._navigate_to(target_section, intent=intent)

    # ###### ПЛАНУВАЛЬНИК НОВИН / NEWS REFRESH SCHEDULER ######
    def _schedule_news_refresh(self) -> None:
        """Schedules daily automatic news refresh based on saved settings."""

        from datetime import datetime, timedelta

        try:
            workspace = load_system_settings_workspace(self._app_context.database_path)
            refresh_time_str = workspace.news_refresh_time or "09:00"
            hour, minute = (int(p) for p in refresh_time_str.split(":"))
        except Exception:  # noqa: BLE001
            hour, minute = 9, 0

        now = datetime.now()
        next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if next_run <= now:
            next_run += timedelta(days=1)

        delay_ms = int((next_run - now).total_seconds() * 1000)
        self._news_timer.stop()
        self._news_timer.start(delay_ms)

    def _install_time_tracking(self) -> None:
        """Tracks system time changes for time-sensitive sections."""

        self._time_tracking_timer = QTimer(self)
        self._time_tracking_timer.setInterval(60 * 1000)
        self._time_tracking_timer.timeout.connect(self._sync_time_sensitive_views_on_timer)
        self._time_tracking_timer.start()

    def _install_manual_report_reminder(self) -> None:
        """Schedules periodic checks for the manual daily report reminder."""

        self._manual_report_timer = QTimer(self)
        self._manual_report_timer.setInterval(60 * 1000)
        self._manual_report_timer.timeout.connect(self._check_manual_report_reminder)
        self._manual_report_timer.start()
        QTimer.singleShot(3000, self._check_manual_report_reminder)

    def _build_time_sync_marker(self) -> tuple[int, int, int, int, int]:
        from datetime import datetime

        now = datetime.now()
        return now.year, now.month, now.day, now.hour, now.minute

    def _build_day_sync_marker(self) -> tuple[int, int, int]:
        from datetime import datetime

        now = datetime.now()
        return now.year, now.month, now.day

    def _sync_time_sensitive_views_on_timer(self) -> None:
        current_day_marker = self._build_day_sync_marker()
        if current_day_marker == self._last_day_sync_marker:
            return
        self._last_day_sync_marker = current_day_marker
        self._sync_time_sensitive_views()

    def _sync_time_sensitive_views(self) -> None:
        marker = self._build_time_sync_marker()
        if marker == self._last_time_sync_marker:
            return
        self._last_time_sync_marker = marker

        current_screen = self._current_screen_widget()
        if current_screen is None or self._has_active_editor_focus():
            return

        if hasattr(current_screen, "_reload_workspace"):
            current_screen._reload_workspace()
            return

        if self._current_section is not None:
            self._navigate_to(
                self._current_section,
                intent=self._current_navigation_intent,
                record_history=False,
            )

    def changeEvent(self, event) -> None:  # type: ignore[override]
        super().changeEvent(event)
        if event.type() == event.Type.ActivationChange and self.isActiveWindow():
            self._sync_time_sensitive_views()
            self._check_manual_report_reminder()

    def _current_screen_widget(self) -> QWidget | None:
        layout = self._content_container.content_layout()
        if layout.count() <= 0:
            return None
        item = layout.itemAt(0)
        return item.widget() if item is not None else None

    def _refresh_news_related_views(self) -> None:
        """Refreshes the current news-related screen without disrupting active input."""

        if self._has_active_editor_focus():
            return
        if self._current_section == AppSection.NEWS_NPA:
            current_screen = self._current_screen_widget()
            if current_screen is not None and hasattr(current_screen, "_reload_workspace"):
                current_screen._reload_workspace()
            return
        if self._current_section == AppSection.DASHBOARD:
            self._navigate_to(
                AppSection.DASHBOARD,
                intent=self._current_navigation_intent,
                record_history=False,
            )

    def _on_news_refresh_schedule_saved(self, _refresh_time: str) -> None:
        """Applies the updated daily news schedule immediately for the running session."""

        self._schedule_news_refresh()

    def _on_news_refresh_completed(self, _payload: object) -> None:
        """Refreshes visible news-related views after a scheduled or manual news update."""

        self._refresh_news_related_views()

    def _on_news_refresh_failed(self, _message_text: str) -> None:
        """Keeps the next timer active after a failed background refresh."""

        self._schedule_news_refresh()

    def _has_active_editor_focus(self) -> bool:
        return isinstance(self.focusWidget(), (QLineEdit, QTextEdit, QComboBox))

    def _check_manual_report_reminder(self) -> None:
        """Checks whether it is time to show the manual report reminder dialog."""

        if self._access_role != AccessRole.INSPECTOR:
            return
        if self._manual_report_prompt_open or self._has_active_editor_focus() or not self.isVisible() or not self.isActiveWindow():
            return
        if not should_prompt_manual_report(self._app_context.database_path):
            return

        self._manual_report_prompt_open = True
        try:
            user_choice = show_manual_report_prompt_dialog(self)
            if user_choice == "build":
                save_result = save_manual_report_via_dialog(
                    self,
                    self._app_context.database_path,
                    access_role=self._access_role,
                )
                if save_result is None:
                    self._postpone_manual_report_prompt()
                else:
                    self._sync_time_sensitive_views()
                return
            if user_choice == "skip":
                self._skip_manual_report_for_today()
                return
            self._postpone_manual_report_prompt()
        finally:
            self._manual_report_prompt_open = False

    def _postpone_manual_report_prompt(self) -> None:
        """Moves the next manual report reminder 30 minutes forward."""

        manual_report_settings = load_manual_report_settings(self._app_context.database_path)
        postponed_settings = ManualReportSettings(
            manual_reminder_enabled=manual_report_settings.manual_reminder_enabled,
            manual_reminder_time=manual_report_settings.manual_reminder_time,
            last_generated_date=manual_report_settings.last_generated_date,
            last_skipped_date=manual_report_settings.last_skipped_date,
            next_prompt_at=(datetime.now() + timedelta(minutes=30)).isoformat(timespec="minutes"),
            default_save_directory=manual_report_settings.default_save_directory,
            ask_save_path_each_time=manual_report_settings.ask_save_path_each_time,
        )
        save_manual_report_settings(
            self._app_context.database_path,
            postponed_settings,
            access_role=self._access_role,
        )

    def _skip_manual_report_for_today(self) -> None:
        """Marks today's manual report reminder as skipped."""

        manual_report_settings = load_manual_report_settings(self._app_context.database_path)
        skipped_settings = ManualReportSettings(
            manual_reminder_enabled=manual_report_settings.manual_reminder_enabled,
            manual_reminder_time=manual_report_settings.manual_reminder_time,
            last_generated_date=manual_report_settings.last_generated_date,
            last_skipped_date=datetime.now().strftime("%Y-%m-%d"),
            next_prompt_at="",
            default_save_directory=manual_report_settings.default_save_directory,
            ask_save_path_each_time=manual_report_settings.ask_save_path_each_time,
        )
        save_manual_report_settings(
            self._app_context.database_path,
            skipped_settings,
            access_role=self._access_role,
        )

    # ###### ЗАПУСК ЗАПЛАНОВАНОЇ ПЕРЕВІРКИ / RUN SCHEDULED NEWS REFRESH ######
    def _run_scheduled_news_refresh(self) -> None:
        """Runs the scheduled news refresh and re-schedules the next one."""

        if self._news_task_controller.start_worker(
            NewsRefreshWorker(self._app_context.database_path, self._access_role)
        ):
            self._schedule_news_refresh()
            return
        QTimer.singleShot(5 * 60 * 1000, self._schedule_news_refresh)


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
