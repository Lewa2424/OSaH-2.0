from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QLabel, QSplitter, QVBoxLayout, QWidget

from osah.application.services.load_audit_log_entries import load_audit_log_entries
from osah.application.services.load_mail_settings import load_mail_settings
from osah.application.services.save_mail_settings import save_mail_settings
from osah.domain.entities.mail_settings import MailSettings
from osah.ui.qt.components.form_feedback_label import FormFeedbackLabel
from osah.ui.qt.components.scrollable_table_frame import ScrollableTableFrame
from osah.ui.qt.components.section_header import SectionHeader
from osah.ui.qt.components.task_progress_widget import TaskProgressWidget
from osah.ui.qt.design.tokens import SPACING
from osah.ui.qt.screens.reports.mail_settings_form import MailSettingsForm
from osah.ui.qt.screens.reports.report_delivery_panel import ReportDeliveryPanel
from osah.ui.qt.screens.reports.report_history_table import ReportHistoryTable
from osah.ui.qt.workers.daily_report_worker import DailyReportWorker
from osah.ui.qt.workers.worker_task_controller import WorkerTaskController


class ReportsScreen(QWidget):
    """Screen for mail settings and daily report delivery flow."""

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
                "Звіти та пошта",
                "Службовий зовнішній контур: формування щоденного звіту, SMTP-доставка, повтори та manual fallback.",
            )
        )

        self.feedback = FormFeedbackLabel()
        layout.addWidget(self.feedback)

        self._task_progress = TaskProgressWidget()
        layout.addWidget(self._task_progress)

        splitter = QSplitter()
        splitter.setChildrenCollapsible(False)

        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        self.settings_form = MailSettingsForm(self._mail_settings)
        self.settings_form.save_requested.connect(self._save_settings)
        left_layout.addWidget(self.settings_form)

        self.delivery_panel = ReportDeliveryPanel()
        self.delivery_panel.build_report_requested.connect(self._build_report)
        self.delivery_panel.send_report_requested.connect(self._send_report)
        self.delivery_panel.open_fallback_requested.connect(self._open_fallback)
        left_layout.addWidget(self.delivery_panel)
        splitter.addWidget(left)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        history_title = QLabel("Історія службових подій доставки")
        history_title.setProperty("role", "section_title")
        right_layout.addWidget(history_title)
        self.history_table = ReportHistoryTable()
        right_layout.addWidget(ScrollableTableFrame(self.history_table))
        splitter.addWidget(right)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        layout.addWidget(splitter, stretch=1)

        self._reload_state()

    # ###### ЗБЕРЕЖЕННЯ НАЛАШТУВАНЬ ПОШТИ / SAVE MAIL SETTINGS ######
    def _save_settings(self, mail_settings: MailSettings) -> None:
        """Saves SMTP settings without blocking user flow."""

        save_mail_settings(
            self._database_path,
            MailSettings(
                daily_report_enabled=mail_settings.daily_report_enabled,
                smtp_host=mail_settings.smtp_host,
                smtp_port=mail_settings.smtp_port,
                smtp_username=mail_settings.smtp_username,
                smtp_password=mail_settings.smtp_password,
                sender_email=mail_settings.sender_email,
                recipient_email=mail_settings.recipient_email,
                use_tls=mail_settings.use_tls,
                last_sent_date=self._mail_settings.last_sent_date,
                daily_report_time=mail_settings.daily_report_time,
            ),
        )
        self.feedback.show_success("Налаштування пошти збережено.")
        self._reload_state()

    # ###### ФОРМУВАННЯ ЗВІТУ У ФОНІ / BUILD REPORT IN BACKGROUND ######
    def _build_report(self) -> None:
        """Starts background report file build operation."""

        if not self._task_controller.start_worker(DailyReportWorker(self._database_path, operation_kind="build")):
            self.feedback.show_error("Операція вже виконується. Дочекайтеся завершення.")

    # ###### НАДСИЛАННЯ ЗВІТУ У ФОНІ / SEND REPORT IN BACKGROUND ######
    def _send_report(self) -> None:
        """Starts background report sending operation."""

        if not self._task_controller.start_worker(DailyReportWorker(self._database_path, operation_kind="send")):
            self.feedback.show_error("Операція вже виконується. Дочекайтеся завершення.")

    # ###### ВІДКРИТТЯ FALLBACK-ФАЙЛУ / OPEN FALLBACK FILE ######
    def _open_fallback(self) -> None:
        """Opens fallback file for manual sending scenario."""

        if self._last_fallback_path is None:
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(self._last_fallback_path)))
        self.feedback.show_success("Файл для ручної відправки відкрито.")

    # ###### СТАРТ ФОНОВОЇ ЗАДАЧІ / BACKGROUND TASK START ######
    def _on_task_started(self) -> None:
        """Applies busy-state at task start."""

        self._task_progress.show_indeterminate("Операцію запущено, виконується у фоні...")
        self.settings_form.setEnabled(False)
        self.delivery_panel.setEnabled(False)

    # ###### ПРОГРЕС ФОНОВОЇ ЗАДАЧІ / BACKGROUND TASK PROGRESS ######
    def _on_task_progress(self, progress_value: int, message_text: str) -> None:
        """Updates progress widget while task is active."""

        self._task_progress.show_progress(message_text, progress_value)

    # ###### УСПІХ ФОНОВОЇ ЗАДАЧІ / BACKGROUND TASK SUCCESS ######
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
            if self._last_report_path is not None:
                self.feedback.show_success(f"Звіт сформовано: {self._last_report_path}")
            else:
                self.feedback.show_error("Файл звіту не сформовано.")
        elif operation_kind == "send":
            if self._last_fallback_path is not None:
                self.feedback.show_error(
                    "Поштову доставку не виконано після 3 спроб. Доступний fallback-файл для ручної відправки."
                )
            else:
                self.feedback.show_success("Щоденний звіт успішно відправлено.")
        self._reload_state()

    # ###### ПОМИЛКА ФОНОВОЇ ЗАДАЧІ / BACKGROUND TASK ERROR ######
    def _on_task_error(self, message_text: str) -> None:
        """Shows background operation error to user."""

        self.feedback.show_error(message_text)

    # ###### ФІНАЛ ФОНОВОЇ ЗАДАЧІ / BACKGROUND TASK FINISH ######
    def _on_task_finished(self) -> None:
        """Resets busy-state after task completion."""

        self._task_progress.hide_state()
        self.settings_form.setEnabled(True)
        self.delivery_panel.setEnabled(True)

    # ###### ОНОВЛЕННЯ ЕКРАНУ / RELOAD SCREEN ######
    def _reload_state(self) -> None:
        """Reloads mail settings, panel state and delivery event history."""

        self._mail_settings = load_mail_settings(self._database_path)
        self.delivery_panel.set_state(self._mail_settings, self._last_report_path, self._last_fallback_path)
        self.history_table.set_entries(load_audit_log_entries(self._database_path, limit=80))
