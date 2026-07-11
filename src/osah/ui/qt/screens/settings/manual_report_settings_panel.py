from PySide6.QtCore import QTime, Signal
from PySide6.QtWidgets import QCheckBox, QHBoxLayout, QLabel, QPushButton, QTimeEdit, QVBoxLayout

from osah.domain.entities.manual_report_settings import ManualReportSettings
from osah.ui.qt.design.tokens import COLOR, RADIUS, SPACING
from osah.ui.qt.screens.settings.settings_section_card import SettingsSectionCard


class ManualReportSettingsPanel(SettingsSectionCard):
    """Секція налаштувань ручного щоденного звіту.
    Settings section for the manual daily report workflow.
    """

    save_requested = Signal(ManualReportSettings)

    def __init__(self, manual_report_settings: ManualReportSettings, read_only: bool) -> None:
        super().__init__()
        self._read_only = read_only
        self._base_settings = manual_report_settings
        layout = self.content_layout()

        title = QLabel("Щоденний звіт")
        title.setProperty("role", "section_title")
        layout.addWidget(title)

        help_label = QLabel(
            "ClearWork не надсилає звіт автоматично. У заданий час програма нагадає сформувати файл звіту. "
            "Після збереження користувач може самостійно надіслати файл будь-яким зручним способом."
        )
        help_label.setWordWrap(True)
        help_label.setStyleSheet(f"color: {COLOR['text_muted']}; font-style: italic;")
        layout.addWidget(help_label)

        self._enabled = QCheckBox("Нагадувати про формування щоденного звіту")
        self._enabled.setChecked(manual_report_settings.manual_reminder_enabled)
        layout.addWidget(self._enabled)

        time_row = QHBoxLayout()
        time_row.setSpacing(SPACING["md"])
        time_title = QLabel("Час нагадування")
        time_row.addWidget(time_title)
        self._time = QTimeEdit()
        self._time.setDisplayFormat("HH:mm")
        parsed_time = QTime.fromString(manual_report_settings.manual_reminder_time or "08:00", "HH:mm")
        self._time.setTime(parsed_time if parsed_time.isValid() else QTime(8, 0))
        self._time.setFixedWidth(140)
        self._time.setButtonSymbols(QTimeEdit.ButtonSymbols.NoButtons)
        self._time.setStyleSheet(
            f"""
            QTimeEdit {{
                min-height: 40px;
                background:
                    qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 rgba(255, 255, 255, 250),
                        stop:1 rgba(241, 246, 251, 242));
                color: {COLOR['text_primary']};
                border: 1px solid #C8D6E5;
                border-radius: {RADIUS['lg']}px;
                padding: 0 14px;
                font-size: 15px;
                font-weight: 700;
                selection-background-color: {COLOR['accent_soft']};
                selection-color: {COLOR['text_primary']};
            }}
            QTimeEdit:focus {{
                border: 1px solid {COLOR['accent']};
                background: #FCFEFF;
            }}
            QTimeEdit:disabled {{
                background: {COLOR['input_disabled_bg']};
                color: {COLOR['input_disabled_text']};
                border: 1px solid {COLOR['input_disabled_border']};
            }}
            """
        )
        time_row.addWidget(self._time)

        time_hint = QLabel("У цей час ClearWork покаже запит на формування файла звіту.")
        time_hint.setWordWrap(True)
        time_hint.setStyleSheet(f"color: {COLOR['text_muted']}; font-style: italic;")
        time_row.addWidget(time_hint, stretch=1)
        layout.addLayout(time_row)

        save_button = QPushButton("Зберегти налаштування звіту")
        save_button.setProperty("variant", "accent")
        save_button.setEnabled(not read_only)
        save_button.clicked.connect(self._emit_save)
        layout.addWidget(save_button)

        self._save_button = save_button
        self._apply_read_only()

    def _apply_read_only(self) -> None:
        """Застосовує режим лише для читання для керівника.
        Applies read-only restrictions for the manager role.
        """

        self._enabled.setEnabled(not self._read_only)
        self._time.setEnabled(not self._read_only)
        self._save_button.setEnabled(not self._read_only)

    def _emit_save(self) -> None:
        """Збирає значення форми та передає їх на збереження.
        Collects the form values and emits them for saving.
        """

        self.save_requested.emit(
            ManualReportSettings(
                manual_reminder_enabled=self._enabled.isChecked(),
                manual_reminder_time=self._time.time().toString("HH:mm"),
                last_generated_date=self._base_settings.last_generated_date,
                last_skipped_date=self._base_settings.last_skipped_date,
                next_prompt_at=self._base_settings.next_prompt_at,
                default_save_directory=self._base_settings.default_save_directory,
                ask_save_path_each_time=self._base_settings.ask_save_path_each_time,
                last_saved_file_path=self._base_settings.last_saved_file_path,
            )
        )
