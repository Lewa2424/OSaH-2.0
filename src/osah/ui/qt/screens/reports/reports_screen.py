import os
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from osah.application.services.load_audit_log_entries import load_audit_log_entries
from osah.application.services.load_mail_settings import load_mail_settings
from osah.domain.services.describe_report_delivery_failure import describe_report_delivery_failure
from osah.ui.qt.components.form_feedback_label import FormFeedbackLabel
from osah.ui.qt.components.scrollable_table_frame import ScrollableTableFrame
from osah.ui.qt.components.section_header import SectionHeader
from osah.ui.qt.components.task_progress_widget import TaskProgressWidget
from osah.ui.qt.design.tokens import SPACING
from osah.ui.qt.screens.reports.report_delivery_panel import ReportDeliveryPanel
from osah.ui.qt.screens.reports.report_history_detail_panel import ReportHistoryDetailPanel
from osah.ui.qt.screens.reports.report_history_table import ReportHistoryTable
from osah.ui.qt.workers.daily_report_worker import DailyReportWorker
from osah.ui.qt.workers.worker_task_controller import WorkerTaskController


class ReportsScreen(QWidget):
    """Screen for daily report operations, state and delivery history."""

    def __init__(self, database_path: Path) -> None:
        super().__init__()
        self._database_path = database_path
        self._mail_settings = load_mail_settings(database_path)
        self._last_report_path: Path | None = None
        self._last_fallback_path: Path | None = None

        self._task_controller = WorkerTaskController()
        self._task_controller.started.connect(self._on_task_started)
        self._task_controller.progress.connect(self._on_task_progress)
        self._task_controller.success.connect(self._on_task_success)
        self._task_controller.error.connect(self._on_task_error)
        self._task_controller.finished.connect(self._on_task_finished)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["xl"], SPACING["lg"], SPACING["xl"], SPACING["lg"])
        layout.setSpacing(SPACING["lg"])

        layout.addWidget(
            SectionHeader(
                "Звіти",
                "Щоденний звіт, поточний стан доставки, ручні дії та історія службових подій.",
            )
        )

        self.feedback = FormFeedbackLabel()
        layout.addWidget(self.feedback)

        self._task_progress = TaskProgressWidget()
        layout.addWidget(self._task_progress)

        self.delivery_panel = ReportDeliveryPanel()
        self.delivery_panel.build_report_requested.connect(self._build_report)
        self.delivery_panel.open_report_requested.connect(self._open_report)
        self.delivery_panel.send_report_requested.connect(self._send_report)
        self.delivery_panel.open_fallback_requested.connect(self._open_fallback)
        layout.addWidget(self.delivery_panel)

        history_hint = QLabel("Список нижче показує спроби відправки й формування звітів. Натисніть рядок, щоб побачити подробиці.")
        history_hint.setWordWrap(True)
        history_hint.setStyleSheet("font-style: italic;")
        layout.addWidget(history_hint)

        history_title = QLabel("Історія службових подій доставки")
        history_title.setProperty("role", "section_title")
        layout.addWidget(history_title)

        self.history_table = ReportHistoryTable()
        self.history_table.entry_selected.connect(self._sync_history_detail_panel)
        layout.addWidget(ScrollableTableFrame(self.history_table), stretch=1)

        self.history_detail_panel = ReportHistoryDetailPanel()
        layout.addWidget(self.history_detail_panel)

        self._reload_state()

    def _build_report(self) -> None:
        """Starts background report file build operation."""

        if not self._task_controller.start_worker(DailyReportWorker(self._database_path, operation_kind="build")):
            self.feedback.show_error("Операція вже виконується. Дочекайтеся завершення.")

    def _open_report(self) -> None:
        """Opens the latest generated report copy."""

        if self._last_report_path is None:
            self.feedback.show_error("Файл звіту ще не сформовано.")
            return
        if not self._open_local_path(self._last_report_path):
            self.feedback.show_error(f"Не вдалося відкрити файл звіту: {self._last_report_path}")
            return
        self.feedback.show_success("Файл звіту відкрито.")

    def _send_report(self) -> None:
        """Starts background report sending operation."""

        if not self._task_controller.start_worker(DailyReportWorker(self._database_path, operation_kind="send")):
            self.feedback.show_error("Операція вже виконується. Дочекайтеся завершення.")

    def _open_fallback(self) -> None:
        """Opens fallback file for manual sending scenario."""

        if self._last_fallback_path is None:
            self.feedback.show_error("Fallback-файл для ручної відправки ще не створено.")
            return
        if not self._open_local_path(self._last_fallback_path):
            self.feedback.show_error(f"Не вдалося відкрити fallback-файл: {self._last_fallback_path}")
            return
        self.feedback.show_success("Файл для ручної відправки відкрито.")

    def _on_task_started(self) -> None:
        """Applies busy-state at task start."""

        self._task_progress.show_indeterminate("Операцію запущено, виконується у фоні...")
        self.delivery_panel.setEnabled(False)

    def _on_task_progress(self, progress_value: int, message_text: str) -> None:
        """Updates progress widget while task is active."""

        self._task_progress.show_progress(message_text, progress_value)

    def _on_task_success(self, payload: object) -> None:
        """Processes worker result payload and updates UI."""

        if not isinstance(payload, dict):
            self.feedback.show_error("Отримано некоректний результат фонового сценарію.")
            return

        report_path = payload.get("report_path")
        fallback_path = payload.get("fallback_path")
        operation_kind = payload.get("operation_kind")
        self._last_report_path = report_path if isinstance(report_path, Path) else None
        self._last_fallback_path = fallback_path if isinstance(fallback_path, Path) else None

        if operation_kind == "build":
            self._reload_state()
            if self._last_report_path is not None:
                self.feedback.show_success(f"Звіт сформовано: {self._last_report_path}")
            else:
                self.feedback.show_error("Файл звіту не сформовано.")
            return

        if operation_kind == "send":
            self._reload_state()
            if self._last_fallback_path is not None:
                self.feedback.show_error(self._build_send_failure_feedback())
            else:
                self.feedback.show_success("Щоденний звіт успішно відправлено.")

    def _on_task_error(self, message_text: str) -> None:
        """Shows background operation error to user."""

        self.feedback.show_error(message_text)

    def _on_task_finished(self) -> None:
        """Resets busy-state after task completion."""

        self._task_progress.hide_state()
        self.delivery_panel.setEnabled(True)

    def _reload_state(self) -> None:
        """Reloads mail settings, panel state and delivery event history."""

        self._mail_settings = load_mail_settings(self._database_path)
        self.delivery_panel.set_state(self._mail_settings, self._last_report_path, self._last_fallback_path)
        self.history_table.set_entries(load_audit_log_entries(self._database_path, limit=80))
        self._sync_history_detail_panel(-1)

    def _sync_history_detail_panel(self, _entry_id: int) -> None:
        """Updates detail panel from the currently selected history entry."""

        current_entry = self.history_table.current_entry()
        if current_entry is None:
            self.history_detail_panel.show_placeholder()
            return
        self.history_detail_panel.set_entry(current_entry)

    def _build_send_failure_feedback(self) -> str:
        """Builds a user-facing explanation for the latest failed send attempt."""

        current_entry = self.history_table.current_entry()
        if current_entry is None:
            return "Поштову доставку не виконано після 3 спроб. Доступний fallback-файл для ручної відправки."
        failure_text = describe_report_delivery_failure(current_entry.description_text)
        return (
            "Поштову доставку не виконано після 3 спроб. "
            f"Причина: {failure_text} Доступний fallback-файл для ручної відправки."
        )

    def _open_local_path(self, local_path: Path) -> bool:
        """Opens a local file in the default desktop application and returns whether the request was accepted."""

        if not local_path.exists():
            return False
        if hasattr(os, "startfile"):
            try:
                os.startfile(str(local_path))
                return True
            except OSError:
                pass
        return QDesktopServices.openUrl(QUrl.fromLocalFile(str(local_path)))
