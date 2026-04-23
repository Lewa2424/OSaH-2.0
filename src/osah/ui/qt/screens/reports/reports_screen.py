from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QLabel, QHBoxLayout, QSplitter, QVBoxLayout, QWidget

from osah.application.services.load_audit_log_entries import load_audit_log_entries
from osah.application.services.load_mail_settings import load_mail_settings
from osah.application.services.save_daily_report_document_copy import save_daily_report_document_copy
from osah.application.services.save_mail_settings import save_mail_settings
from osah.application.services.send_daily_report_email import send_daily_report_email
from osah.domain.entities.mail_settings import MailSettings
from osah.ui.qt.components.form_feedback_label import FormFeedbackLabel
from osah.ui.qt.design.tokens import COLOR, SPACING
from osah.ui.qt.screens.reports.mail_settings_form import MailSettingsForm
from osah.ui.qt.screens.reports.report_delivery_panel import ReportDeliveryPanel
from osah.ui.qt.screens.reports.report_history_table import ReportHistoryTable


class ReportsScreen(QWidget):
    """Екран пошти, щоденного звіту та службових помилок доставки.
    Screen for mail, daily report, and delivery service errors.
    """

    def __init__(self, database_path: Path) -> None:
        super().__init__()
        self._database_path = database_path
        self._mail_settings = load_mail_settings(database_path)
        self._last_report_path: Path | None = None
        self._last_fallback_path: Path | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["xl"], SPACING["lg"], SPACING["xl"], SPACING["lg"])
        layout.setSpacing(SPACING["lg"])

        title = QLabel("Звіти та пошта")
        title.setStyleSheet("font-size: 22px; font-weight: 900;")
        layout.addWidget(title)

        subtitle = QLabel(
            "Зовнішній службовий контур: формування щоденного звіту, SMTP-доставка, повтори та ручний fallback."
        )
        subtitle.setStyleSheet(f"color: {COLOR['text_secondary']};")
        layout.addWidget(subtitle)

        self.feedback = FormFeedbackLabel()
        layout.addWidget(self.feedback)

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
        right_layout.addWidget(self.history_table)
        splitter.addWidget(right)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        layout.addWidget(splitter, stretch=1)

        self._reload_state()

    # ###### ЗБЕРЕЖЕННЯ НАЛАШТУВАНЬ / SAVE SETTINGS ######
    def _save_settings(self, mail_settings: MailSettings) -> None:
        """Зберігає SMTP-параметри без запису секретів у audit-опис.
        Saves SMTP settings without writing secrets to audit descriptions.
        """

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

    # ###### ФОРМУВАННЯ ЗВІТУ / BUILD REPORT ######
    def _build_report(self) -> None:
        """Формує локальну копію щоденного звіту для перегляду або ручної відправки.
        Builds a local daily report copy for review or manual sending.
        """

        try:
            self._last_report_path = save_daily_report_document_copy(self._database_path)
            self._last_fallback_path = None
            self.feedback.show_success(f"Звіт сформовано: {self._last_report_path}")
        except Exception as error:  # noqa: BLE001
            self.feedback.show_error(f"Не вдалося сформувати звіт: {type(error).__name__}")
        self._reload_state()

    # ###### ВІДПРАВКА ЗВІТУ / SEND REPORT ######
    def _send_report(self) -> None:
        """Запускає SMTP-відправку звіту з трьома спробами та fallback-файлом при провалі.
        Starts SMTP report delivery with three attempts and fallback file on failure.
        """

        try:
            self._last_report_path, self._last_fallback_path = send_daily_report_email(self._database_path)
            if self._last_fallback_path:
                self.feedback.show_error(
                    "Поштову доставку не виконано після 3 спроб. Доступний файл для ручної відправки."
                )
            else:
                self.feedback.show_success("Щоденний звіт успішно відправлено.")
        except Exception as error:  # noqa: BLE001
            self.feedback.show_error(f"Відправку зупинено: {error}")
        self._reload_state()

    # ###### РУЧНИЙ FALLBACK / MANUAL FALLBACK ######
    def _open_fallback(self) -> None:
        """Відкриває fallback-файл або каталог для ручної відправки звіту.
        Opens fallback file or folder for manual report sending.
        """

        if self._last_fallback_path is None:
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(self._last_fallback_path)))
        self.feedback.show_success("Файл для ручної відправки відкрито. Службову доставку перехоплено вручну.")

    # ###### ОНОВЛЕННЯ ЕКРАНУ / RELOAD SCREEN ######
    def _reload_state(self) -> None:
        """Оновлює налаштування, панель доставки та історію службових подій.
        Reloads settings, delivery panel, and service event history.
        """

        self._mail_settings = load_mail_settings(self._database_path)
        self.delivery_panel.set_state(self._mail_settings, self._last_report_path, self._last_fallback_path)
        self.history_table.set_entries(load_audit_log_entries(self._database_path, limit=80))
