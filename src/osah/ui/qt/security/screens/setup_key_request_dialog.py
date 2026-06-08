"""Діалог формування запиту на ключ установки / Setup key request dialog."""

from pathlib import Path

from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
)

from osah.application.services.security.save_setup_key_request_report import save_setup_key_request_report
from osah.domain.services.setup_key.build_setup_key_request_default_file_name import (
    build_setup_key_request_default_file_name,
)
from osah.domain.services.setup_key.build_setup_key_request_report import SetupKeyRequestReportInput
from osah.infrastructure.config.support_contacts import SUPPORT_EMAIL, SUPPORT_PHONE
from osah.ui.qt.design.tokens import COLOR, RADIUS, SPACING


class SetupKeyRequestDialog(QDialog):
    """Анкета для збереження текстового запиту на ключ установки."""

    def __init__(self, parent, installation_id: str, data_directory: Path) -> None:
        super().__init__(parent)
        self._installation_id = installation_id
        self._data_directory = data_directory
        self.setWindowTitle("Запит на ключ установки")
        self.setMinimumWidth(640)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["lg"], SPACING["lg"], SPACING["lg"], SPACING["lg"])
        layout.setSpacing(SPACING["md"])

        intro = QLabel(
            "Заповніть коротку анкету та збережіть текстовий файл. Надішліть його розробнику "
            "для отримання ключа установки ClearWork."
        )
        intro.setWordWrap(True)
        intro.setFont(QFont("Segoe UI", 11))
        intro.setStyleSheet(f"color: {COLOR['text_secondary']};")
        layout.addWidget(intro)

        form = QFormLayout()
        form.setSpacing(SPACING["sm"])

        self._installation_id_field = QLineEdit(self._installation_id)
        self._installation_id_field.setReadOnly(True)
        self._enterprise_input = QLineEdit()
        self._enterprise_input.setPlaceholderText("ТОВ «Приклад»")
        self._contact_person_input = QLineEdit()
        self._contact_person_input.setPlaceholderText("ПІБ відповідальної особи")
        self._contact_details_input = QLineEdit()
        self._contact_details_input.setPlaceholderText("email або телефон для відповіді")

        form.addRow("ID установки", self._installation_id_field)
        form.addRow("Підприємство", self._enterprise_input)
        form.addRow("Контактна особа", self._contact_person_input)
        form.addRow("Контакти", self._contact_details_input)
        layout.addLayout(form)

        support_block = QLabel(
            f"Надіслати файл розробнику:\n"
            f"• {SUPPORT_EMAIL}\n"
            f"• {SUPPORT_PHONE}\n\n"
            "Важливо: ключ прив'язаний до ID установки у папці data\\. "
            "Якщо видалити програму разом із data\\, знадобиться новий ключ."
        )
        support_block.setWordWrap(True)
        support_block.setFont(QFont("Segoe UI", 10))
        support_block.setStyleSheet(
            f"color: {COLOR['text_secondary']}; "
            f"background: {COLOR['bg_panel']}; "
            f"border: 1px solid {COLOR['border_soft']}; "
            f"border-radius: {RADIUS['md']}px; "
            f"padding: 12px;"
        )
        layout.addWidget(support_block)

        self._feedback_label = QLabel("")
        self._feedback_label.setWordWrap(True)
        self._feedback_label.setStyleSheet(f"color: {COLOR['danger']};")
        layout.addWidget(self._feedback_label)

        buttons = QDialogButtonBox()
        save_button = buttons.addButton("Зберегти", QDialogButtonBox.ButtonRole.AcceptRole)
        cancel_button = buttons.addButton("Скасувати", QDialogButtonBox.ButtonRole.RejectRole)
        save_button.clicked.connect(self._on_save_clicked)
        cancel_button.clicked.connect(self.reject)
        layout.addWidget(buttons)

    def _on_save_clicked(self) -> None:
        enterprise_name = self._enterprise_input.text().strip()
        contact_person = self._contact_person_input.text().strip()
        contact_details = self._contact_details_input.text().strip()

        if not enterprise_name:
            self._feedback_label.setText("Вкажіть назву підприємства.")
            return
        if not contact_person:
            self._feedback_label.setText("Вкажіть контактну особу.")
            return
        if not contact_details:
            self._feedback_label.setText("Вкажіть email або телефон для відповіді.")
            return

        suggested_path = self._data_directory / build_setup_key_request_default_file_name(self._installation_id)
        selected_path_text, _ = QFileDialog.getSaveFileName(
            self,
            "Зберегти запит на ключ установки",
            str(suggested_path),
            "Text files (*.txt);;All files (*)",
        )
        if not selected_path_text:
            return

        report_input = SetupKeyRequestReportInput(
            installation_id=self._installation_id,
            enterprise_name=enterprise_name,
            contact_person=contact_person,
            contact_details=contact_details,
        )
        try:
            saved_path = save_setup_key_request_report(Path(selected_path_text), report_input)
        except OSError:
            self._feedback_label.setText("Не вдалося зберегти файл.")
            return

        QMessageBox.information(
            self,
            "ClearWork",
            f"Файл збережено:\n{saved_path}\n\nНадішліть його розробнику для отримання ключа.",
        )
        self.accept()
