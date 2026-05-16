from datetime import datetime

from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QVBoxLayout, QWidget

from osah.ui.qt.components.form_feedback_label import FormFeedbackLabel
from osah.ui.qt.design.tokens import COLOR, SPACING


class RecordWorkPermitDailyCheckDialog(QDialog):
    """Модальне вікно фіксації щоденної перевірки місця робіт.
    Modal dialog for recording a daily work-area check.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Щоденна перевірка")
        self.setModal(True)
        self.resize(460, 280)
        self.setStyleSheet(f"QDialog {{ background: {COLOR['bg_card']}; }}")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["lg"], SPACING["lg"], SPACING["lg"], SPACING["lg"])
        layout.setSpacing(SPACING["md"])

        current_moment_text = datetime.now().strftime("%d.%m.%Y %H:%M")
        self._checked_at_input = QLineEdit(current_moment_text)
        self._checked_at_input.setPlaceholderText("ДД.ММ.РРРР HH:MM або YYYY-MM-DD HH:MM")
        layout.addWidget(QLabel("Дата та час перевірки"))
        layout.addWidget(self._checked_at_input)

        self._checked_by_input = QLineEdit()
        self._checked_by_input.setPlaceholderText("Хто виконав перевірку місця робіт")
        layout.addWidget(QLabel("Перевірив"))
        layout.addWidget(self._checked_by_input)

        self._note_input = QTextEdit()
        self._note_input.setMaximumHeight(88)
        self._note_input.setPlaceholderText("За потреби зафіксуйте коротку примітку до щоденної перевірки.")
        layout.addWidget(QLabel("Примітка"))
        layout.addWidget(self._note_input)

        self._feedback_label = FormFeedbackLabel()
        layout.addWidget(self._feedback_label)

        buttons_row = QHBoxLayout()
        cancel_button = QPushButton("Скасувати")
        cancel_button.setProperty("variant", "secondary")
        cancel_button.clicked.connect(self.reject)
        buttons_row.addWidget(cancel_button)
        buttons_row.addStretch()

        save_button = QPushButton("Зафіксувати")
        save_button.setProperty("variant", "accent")
        save_button.clicked.connect(self._accept_if_valid)
        buttons_row.addWidget(save_button)
        layout.addLayout(buttons_row)

    def checked_at_text(self) -> str:
        """Повертає введені дату та час перевірки.
        Returns the entered daily-check datetime.
        """

        return self._checked_at_input.text().strip()

    def checked_by_text(self) -> str:
        """Повертає введене ім'я відповідального за перевірку.
        Returns the entered check operator name.
        """

        return self._checked_by_input.text().strip()

    def note_text(self) -> str:
        """Повертає введену примітку до перевірки.
        Returns the entered daily-check note.
        """

        return self._note_input.toPlainText().strip()

    def _accept_if_valid(self) -> None:
        """Перевіряє обов'язкові поля перед збереженням.
        Validates required fields before saving.
        """

        if not self.checked_at_text():
            self._feedback_label.show_error("Потрібно вказати дату та час щоденної перевірки.")
            return
        if not self.checked_by_text():
            self._feedback_label.show_error("Потрібно вказати, хто виконав щоденну перевірку.")
            return
        self.accept()
