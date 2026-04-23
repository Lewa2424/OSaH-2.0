from PySide6.QtCore import QTime, Signal
from PySide6.QtWidgets import QCheckBox, QFormLayout, QLineEdit, QPushButton, QSpinBox, QTimeEdit, QVBoxLayout, QWidget

from osah.domain.entities.mail_settings import MailSettings
from osah.ui.qt.design.tokens import SPACING


class MailSettingsForm(QWidget):
    """Форма налаштувань поштового контуру та часу щоденного звіту.
    Form for mail channel settings and daily report time.
    """

    save_requested = Signal(MailSettings)

    def __init__(self, mail_settings: MailSettings) -> None:
        super().__init__()
        self.enabled_box = QCheckBox("Автощоденний звіт увімкнено")
        self.enabled_box.setChecked(mail_settings.daily_report_enabled)

        self.report_time = QTimeEdit()
        self.report_time.setDisplayFormat("HH:mm")
        parsed_time = QTime.fromString(mail_settings.daily_report_time or "08:00", "HH:mm")
        self.report_time.setTime(parsed_time if parsed_time.isValid() else QTime(8, 0))

        self.recipient = QLineEdit(mail_settings.recipient_email)
        self.sender = QLineEdit(mail_settings.sender_email)
        self.smtp_host = QLineEdit(mail_settings.smtp_host)
        self.smtp_port = QSpinBox()
        self.smtp_port.setRange(1, 65535)
        self.smtp_port.setValue(mail_settings.smtp_port if mail_settings.smtp_port > 0 else 587)
        self.smtp_username = QLineEdit(mail_settings.smtp_username)
        self.smtp_password = QLineEdit(mail_settings.smtp_password)
        self.smtp_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.use_tls = QCheckBox("TLS")
        self.use_tls.setChecked(mail_settings.use_tls)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING["md"])

        form = QFormLayout()
        form.addRow("", self.enabled_box)
        form.addRow("Час відправки", self.report_time)
        form.addRow("Керівник / отримувач", self.recipient)
        form.addRow("Відправник", self.sender)
        form.addRow("SMTP host", self.smtp_host)
        form.addRow("SMTP port", self.smtp_port)
        form.addRow("SMTP користувач", self.smtp_username)
        form.addRow("SMTP пароль", self.smtp_password)
        form.addRow("", self.use_tls)
        layout.addLayout(form)

        save_button = QPushButton("Зберегти налаштування")
        save_button.clicked.connect(self._emit_save_requested)
        layout.addWidget(save_button)

    # ###### ПІДГОТОВКА НАЛАШТУВАНЬ / BUILD SETTINGS ######
    def values(self, last_sent_date: str = "") -> MailSettings:
        """Повертає MailSettings із поточних полів форми.
        Returns MailSettings from the current form fields.
        """

        return MailSettings(
            daily_report_enabled=self.enabled_box.isChecked(),
            smtp_host=self.smtp_host.text(),
            smtp_port=int(self.smtp_port.value()),
            smtp_username=self.smtp_username.text(),
            smtp_password=self.smtp_password.text(),
            sender_email=self.sender.text(),
            recipient_email=self.recipient.text(),
            use_tls=self.use_tls.isChecked(),
            last_sent_date=last_sent_date,
            daily_report_time=self.report_time.time().toString("HH:mm"),
        )

    # ###### ЗАПИТ ЗБЕРЕЖЕННЯ / SAVE REQUEST ######
    def _emit_save_requested(self) -> None:
        """Передає поточні налаштування екрану для збереження.
        Emits current settings for saving by the screen.
        """

        self.save_requested.emit(self.values())
