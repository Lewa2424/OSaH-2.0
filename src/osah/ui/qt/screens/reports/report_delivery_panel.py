from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QVBoxLayout

from osah.domain.entities.mail_settings import MailSettings
from osah.domain.services.build_mail_recipient_summary import build_mail_recipient_summary
from osah.domain.services.format_ui_date import format_ui_date
from osah.domain.services.is_mail_settings_ready import is_mail_settings_ready
from osah.ui.qt.design.tokens import COLOR, RADIUS, SPACING


class ReportDeliveryPanel(QFrame):
    """Панель стану доставки щоденного звіту та локальних ручних дій.
    Panel for daily report delivery state and local manual actions.
    """

    build_report_requested = Signal()
    open_report_requested = Signal()
    send_report_requested = Signal()
    open_fallback_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.setProperty("card", "true")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["lg"], SPACING["lg"], SPACING["lg"], SPACING["lg"])
        layout.setSpacing(SPACING["lg"])

        title = QLabel("Поточний стан доставки")
        title.setProperty("role", "section_title")
        layout.addWidget(title)

        hint = QLabel("Параметри пошти змінюються у розділі «Налаштування». Тут лише стан і запуск сценаріїв.")
        hint.setWordWrap(True)
        hint.setStyleSheet(f"color: {COLOR['text_muted']}; font-style: italic;")
        layout.addWidget(hint)

        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet(
            f"background: {COLOR['bg_panel']}; border: 1px solid {COLOR['border_soft']}; "
            f"border-radius: {RADIUS['md']}px; padding: {SPACING['md']}px;"
        )
        layout.addWidget(self.status_label)

        self.build_button = QPushButton("Сформувати файл звіту")
        self.build_button.setProperty("variant", "secondary")
        self.build_button.clicked.connect(self.build_report_requested.emit)
        layout.addWidget(self.build_button)

        self.report_button = QPushButton("Відкрити сформований звіт")
        self.report_button.setProperty("variant", "secondary")
        self.report_button.clicked.connect(self.open_report_requested.emit)
        self.report_button.setEnabled(False)
        layout.addWidget(self.report_button)

        self.send_button = QPushButton("Надіслати зараз")
        self.send_button.setProperty("variant", "accent")
        self.send_button.clicked.connect(self.send_report_requested.emit)
        layout.addWidget(self.send_button)

        self.fallback_button = QPushButton("Відкрити файл для ручної відправки")
        self.fallback_button.setProperty("variant", "secondary")
        self.fallback_button.clicked.connect(self.open_fallback_requested.emit)
        self.fallback_button.setEnabled(False)
        layout.addWidget(self.fallback_button)

    def set_state(
        self,
        mail_settings: MailSettings,
        report_copy_path: Path | None,
        fallback_email_path: Path | None,
    ) -> None:
        """Показує поточний стан автозвіту та доступність локальних файлів.
        Shows current auto-report state and local file availability.
        """

        enabled_text = "увімкнено" if mail_settings.daily_report_enabled else "вимкнено"
        ready_text = "готово" if is_mail_settings_ready(mail_settings) else "неповні параметри"
        recipient_text = build_mail_recipient_summary(mail_settings.recipient_email)
        last_sent_text = format_ui_date(mail_settings.last_sent_date.strip()) if mail_settings.last_sent_date.strip() else "ще не відправлявся"
        report_text = report_copy_path.name if report_copy_path else "файл ще не сформовано"
        fallback_text = fallback_email_path.name if fallback_email_path else "не потрібен"
        self.status_label.setText(
            f"Автозвіт: {enabled_text}\n"
            f"Час надсилання: {mail_settings.daily_report_time}\n"
            f"Поштова конфігурація: {ready_text}\n"
            f"Отримувачі: {recipient_text}\n"
            f"Остання успішна відправка: {last_sent_text}\n"
            f"Останній файл звіту: {report_text}\n"
            f"Ручний fallback: {fallback_text}"
        )
        self.report_button.setEnabled(report_copy_path is not None)
        self.fallback_button.setEnabled(fallback_email_path is not None)
