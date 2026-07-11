from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QVBoxLayout

from osah.domain.entities.manual_report_settings import ManualReportSettings
from osah.ui.qt.design.tokens import COLOR, RADIUS, SPACING


class ReportDeliveryPanel(QFrame):
    """Панель стану та дій для ручного щоденного звіту.
    Panel showing state and actions for the manual daily report workflow.
    """

    build_report_requested = Signal()
    open_report_requested = Signal()
    open_reports_directory_requested = Signal()

    def __init__(self, read_only: bool) -> None:
        super().__init__()
        self._read_only = read_only
        self.setObjectName("reportDeliveryPanel")
        self.setStyleSheet(
            f"""
            QFrame#reportDeliveryPanel {{
                background:
                    qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 rgba(255, 255, 255, 246),
                        stop:0.55 rgba(244, 248, 252, 238),
                        stop:1 rgba(232, 240, 248, 228));
                border: 1px solid rgba(129, 163, 197, 0.55);
                border-radius: 26px;
            }}
            QFrame#reportDeliveryPanel QLabel[role="section_title"] {{
                color: {COLOR['text_primary']};
                font-size: 22px;
                font-weight: 800;
            }}
            QFrame#reportDeliveryPanel QLabel {{
                font-size: 15px;
            }}
            QFrame#reportDeliveryPanel QPushButton {{
                min-height: 42px;
                border-radius: {RADIUS['lg']}px;
                font-size: 14px;
                font-weight: 800;
            }}
            """
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["lg"], SPACING["lg"], SPACING["lg"], SPACING["lg"])
        layout.setSpacing(SPACING["lg"])

        title = QLabel("Поточний стан")
        title.setProperty("role", "section_title")
        layout.addWidget(title)

        hint = QLabel(
            "ClearWork формує файл щоденного звіту для подальшої ручної передачі користувачем. "
            "Нагадування та час запиту змінюються у розділі «Налаштування»."
        )
        hint.setWordWrap(True)
        hint.setStyleSheet(f"color: {COLOR['text_muted']}; font-style: italic;")
        layout.addWidget(hint)

        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet(
            f"background: rgba(255, 255, 255, 0.9); border: 1px solid {COLOR['border_soft']}; "
            f"border-radius: {RADIUS['lg']}px; padding: {SPACING['md']}px; font-size: 15px; color: {COLOR['text_secondary']};"
        )
        layout.addWidget(self.status_label)

        self.build_button = QPushButton("Сформувати файл звіту")
        self.build_button.setProperty("variant", "accent")
        self.build_button.clicked.connect(self.build_report_requested.emit)
        self.build_button.setVisible(not self._read_only)
        self.build_button.setEnabled(not self._read_only)
        layout.addWidget(self.build_button)

        self.report_button = QPushButton("Відкрити останній сформований звіт")
        self.report_button.setProperty("variant", "secondary")
        self.report_button.clicked.connect(self.open_report_requested.emit)
        self.report_button.setEnabled(False)
        layout.addWidget(self.report_button)

        self.directory_button = QPushButton("Відкрити папку звітів")
        self.directory_button.setProperty("variant", "secondary")
        self.directory_button.clicked.connect(self.open_reports_directory_requested.emit)
        layout.addWidget(self.directory_button)

    def set_state(
        self,
        manual_report_settings: ManualReportSettings,
        latest_report_path: Path | None,
        last_action_text: str,
    ) -> None:
        """Показує стан нагадування та відомості про останній сформований звіт.
        Shows reminder state and information about the latest generated report.
        """

        enabled_text = "увімкнено" if manual_report_settings.manual_reminder_enabled else "вимкнено"
        report_text = latest_report_path.name if latest_report_path is not None else "ще не сформовано"
        self.status_label.setText(
            f"Нагадування: {enabled_text}\n"
            f"Час нагадування: {manual_report_settings.manual_reminder_time}\n"
            f"Остання дія: {last_action_text}\n"
            f"Останній файл звіту: {report_text}"
        )
        self.report_button.setEnabled(latest_report_path is not None)
