from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from osah.domain.entities.mail_settings import MailSettings
from osah.ui.qt.design.tokens import COLOR, RADIUS, SPACING


class ReportDeliveryPanel(QWidget):
    """Панель стану доставки щоденного звіту та ручного fallback-файлу.
    Panel for daily report delivery state and manual fallback file.
    """

    build_report_requested = Signal()
    send_report_requested = Signal()
    open_fallback_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["lg"], SPACING["lg"], SPACING["lg"], SPACING["lg"])
        layout.setSpacing(SPACING["md"])
        self.setStyleSheet(
            f"background: {COLOR['bg_card']}; border: 1px solid {COLOR['border_soft']}; "
            f"border-radius: {RADIUS['lg']}px;"
        )

        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        self.build_button = QPushButton("Сформувати файл звіту")
        self.build_button.clicked.connect(self.build_report_requested.emit)
        layout.addWidget(self.build_button)

        self.send_button = QPushButton("Надіслати зараз")
        self.send_button.clicked.connect(self.send_report_requested.emit)
        layout.addWidget(self.send_button)

        self.fallback_button = QPushButton("Відкрити файл для ручної відправки")
        self.fallback_button.clicked.connect(self.open_fallback_requested.emit)
        self.fallback_button.setEnabled(False)
        layout.addWidget(self.fallback_button)

    # ###### ОНОВЛЕННЯ СТАНУ / UPDATE STATE ######
    def set_state(
        self,
        mail_settings: MailSettings,
        report_copy_path: Path | None,
        fallback_email_path: Path | None,
    ) -> None:
        """Показує поточний стан автоотчіту та доступність ручного сценарію.
        Shows current report state and manual fallback availability.
        """

        enabled_text = "увімкнено" if mail_settings.daily_report_enabled else "вимкнено"
        recipient_text = mail_settings.recipient_email.strip() or "не задано"
        last_sent_text = mail_settings.last_sent_date.strip() or "ще не відправлявся"
        report_text = report_copy_path.name if report_copy_path else "файл ще не сформовано"
        fallback_text = fallback_email_path.name if fallback_email_path else "не потрібен"
        self.status_label.setText(
            "Автоотчіт: "
            f"{enabled_text}\nЧас: {mail_settings.daily_report_time}\nОтримувач: {recipient_text}\n"
            f"Остання успішна дата: {last_sent_text}\nКопія звіту: {report_text}\n"
            f"Ручний fallback: {fallback_text}"
        )
        self.fallback_button.setEnabled(fallback_email_path is not None)
