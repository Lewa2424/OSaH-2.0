from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from osah.ui.qt.components.form_feedback_label import FormFeedbackLabel
from osah.ui.qt.design.tokens import COLOR, SPACING


class AddManualRiskDialog(QDialog):
    """Діалог ручного введення ризику в паспорт.
    Dialog for manually entering a risk into the passport.
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Додати ризик вручну")
        self.setModal(True)
        self.setMinimumWidth(540)
        self.setStyleSheet(f"QDialog {{ background: {COLOR['bg_card']}; }}")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["lg"], SPACING["lg"], SPACING["lg"], SPACING["lg"])
        layout.setSpacing(SPACING["md"])

        form = QFormLayout()
        form.setSpacing(SPACING["sm"])

        self._situation_input = QTextEdit()
        self._situation_input.setPlaceholderText("Опис ризикової ситуації (обов'язково)")
        self._situation_input.setMaximumHeight(80)
        form.addRow("Ризикова ситуація *", self._situation_input)

        self._source_input = QTextEdit()
        self._source_input.setPlaceholderText("Джерело небезпеки")
        self._source_input.setMaximumHeight(60)
        form.addRow("Джерело небезпеки", self._source_input)

        self._conditions_input = QTextEdit()
        self._conditions_input.setPlaceholderText("Умови виникнення")
        self._conditions_input.setMaximumHeight(60)
        form.addRow("Умови виникнення", self._conditions_input)

        self._consequences_input = QTextEdit()
        self._consequences_input.setPlaceholderText("Можливі наслідки")
        self._consequences_input.setMaximumHeight(60)
        form.addRow("Наслідки", self._consequences_input)

        layout.addLayout(form)

        self._feedback = FormFeedbackLabel()
        layout.addWidget(self._feedback)

        buttons = QHBoxLayout()
        cancel_btn = QPushButton("Скасувати")
        cancel_btn.setProperty("variant", "secondary")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(cancel_btn)
        buttons.addStretch()
        save_btn = QPushButton("Зберегти ризик")
        save_btn.setProperty("variant", "accent")
        save_btn.clicked.connect(self._on_save)
        buttons.addWidget(save_btn)
        layout.addLayout(buttons)

    def _on_save(self) -> None:
        if not self._situation_input.toPlainText().strip():
            self._feedback.show_error("Ризикова ситуація є обов'язковою.")
            return
        self.accept()

    def risk_situation(self) -> str:
        return self._situation_input.toPlainText().strip()

    def hazard_source(self) -> str:
        return self._source_input.toPlainText().strip()

    def occurrence_conditions(self) -> str:
        return self._conditions_input.toPlainText().strip()

    def consequences(self) -> str:
        return self._consequences_input.toPlainText().strip()
