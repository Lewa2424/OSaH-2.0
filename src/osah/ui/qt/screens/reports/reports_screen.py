import os
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from osah.application.services.load_audit_log_entries import load_audit_log_entries
from osah.application.services.load_latest_manual_report_file_path import load_latest_manual_report_file_path
from osah.application.services.load_manual_report_settings import load_manual_report_settings
from osah.domain.entities.access_role import AccessRole
from osah.domain.services.build_manual_report_last_action_text import build_manual_report_last_action_text
from osah.ui.qt.components.form_feedback_label import FormFeedbackLabel
from osah.ui.qt.components.scrollable_table_frame import ScrollableTableFrame
from osah.ui.qt.components.section_header import SectionHeader
from osah.ui.qt.design.tokens import SPACING
from osah.ui.qt.screens.reports.report_delivery_panel import ReportDeliveryPanel
from osah.ui.qt.screens.reports.report_history_detail_panel import ReportHistoryDetailPanel
from osah.ui.qt.screens.reports.report_history_table import ReportHistoryTable
from osah.ui.qt.services.save_manual_report_via_dialog import save_manual_report_via_dialog


class ReportsScreen(QWidget):
    """Екран ручного формування щоденного звіту та перегляду його історії.
    Screen for manual daily report generation and viewing its history.
    """

    def __init__(self, database_path: Path, access_role: AccessRole) -> None:
        super().__init__()
        self._database_path = database_path
        self._access_role = access_role
        self._read_only = access_role != AccessRole.INSPECTOR
        self._last_report_path: Path | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["xl"], SPACING["lg"], SPACING["xl"], SPACING["lg"])
        layout.setSpacing(SPACING["lg"])

        layout.addWidget(
            SectionHeader(
                "Звіти",
                "Формування щоденного звіту для ручного збереження та подальшої відправки користувачем.",
            )
        )

        self.feedback = FormFeedbackLabel()
        layout.addWidget(self.feedback)

        self.delivery_panel = ReportDeliveryPanel(read_only=self._read_only)
        self.delivery_panel.build_report_requested.connect(self._build_report)
        self.delivery_panel.open_report_requested.connect(self._open_report)
        self.delivery_panel.open_reports_directory_requested.connect(self._open_reports_directory)
        layout.addWidget(self.delivery_panel)

        history_hint = QLabel(
            "У списку нижче зберігається історія сформованих звітів. "
            "Натисніть рядок, щоб побачити подробиці."
        )
        history_hint.setWordWrap(True)
        history_hint.setStyleSheet("font-style: italic;")
        layout.addWidget(history_hint)

        history_title = QLabel("Історія сформованих звітів")
        history_title.setProperty("role", "section_title")
        layout.addWidget(history_title)

        self.history_table = ReportHistoryTable()
        self.history_table.entry_selected.connect(self._sync_history_detail_panel)
        layout.addWidget(ScrollableTableFrame(self.history_table), stretch=1)

        self.history_detail_panel = ReportHistoryDetailPanel()
        layout.addWidget(self.history_detail_panel)

        self._reload_state()

    def _build_report(self) -> None:
        """Запускає ручне збереження щоденного звіту через системний діалог.
        Starts manual daily report saving through the system file dialog.
        """

        if self._read_only:
            self.feedback.show_error("Режим read-only: формування файлу звіту недоступне.")
            return

        save_result = save_manual_report_via_dialog(
            self,
            self._database_path,
            access_role=self._access_role,
        )
        if save_result is None:
            self.feedback.show_error("Збереження звіту скасовано.")
            return

        self._last_report_path = save_result.internal_copy_path
        self._reload_state()
        self.feedback.show_success(f"Звіт сформовано: {save_result.user_file_path}")

    def _open_report(self) -> None:
        """Відкриває останню внутрішню копію сформованого звіту.
        Opens the latest internal copy of the generated report.
        """

        if self._last_report_path is None:
            self.feedback.show_error("Файл звіту ще не сформовано.")
            return
        if not self._open_local_path(self._last_report_path):
            self.feedback.show_error(f"Не вдалося відкрити файл звіту: {self._last_report_path}")
            return
        self.feedback.show_success("Файл звіту відкрито.")

    def _open_reports_directory(self) -> None:
        """Відкриває внутрішню папку збережених копій звітів.
        Opens the internal directory with saved report copies.
        """

        reports_directory = self._database_path.parent / "reports"
        reports_directory.mkdir(parents=True, exist_ok=True)
        if not self._open_local_path(reports_directory):
            self.feedback.show_error(f"Не вдалося відкрити папку звітів: {reports_directory}")

    def _reload_state(self) -> None:
        """Перезавантажує стан ручного звіту та історію сформованих файлів.
        Reloads manual report state and the generated file history.
        """

        manual_report_settings = load_manual_report_settings(self._database_path)
        self._last_report_path = load_latest_manual_report_file_path(self._database_path)
        self.delivery_panel.set_state(
            manual_report_settings,
            self._last_report_path,
            build_manual_report_last_action_text(manual_report_settings),
        )
        self.history_table.set_entries(load_audit_log_entries(self._database_path, limit=80))
        self._sync_history_detail_panel(-1)

    def _sync_history_detail_panel(self, _entry_id: int) -> None:
        """Оновлює detail-панель за поточним вибраним записом історії.
        Updates the detail panel from the currently selected history entry.
        """

        current_entry = self.history_table.current_entry()
        if current_entry is None:
            self.history_detail_panel.show_placeholder()
            return
        self.history_detail_panel.set_entry(current_entry)

    def _open_local_path(self, local_path: Path) -> bool:
        """Відкриває локальний файл або папку системним застосунком.
        Opens a local file or directory in the default desktop application.
        """

        if not local_path.exists():
            return False
        if hasattr(os, "startfile"):
            try:
                os.startfile(str(local_path))
                return True
            except OSError:
                pass
        return QDesktopServices.openUrl(QUrl.fromLocalFile(str(local_path)))
