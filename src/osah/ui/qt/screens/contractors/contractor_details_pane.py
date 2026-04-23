from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QLabel, QLineEdit, QPushButton, QTextEdit, QVBoxLayout, QWidget

from osah.domain.entities.contractor_record import ContractorRecord


class ContractorDetailsPane(QWidget):
    """Contractor details and editor pane."""

    save_requested = Signal(object)

    def __init__(self, read_only: bool) -> None:
        super().__init__()
        self._read_only = read_only
        self._current_id = ""

        layout = QVBoxLayout(self)
        title = QLabel("Картка підрядника")
        title.setProperty("role", "section_title")
        layout.addWidget(title)

        self._company = QLineEdit()
        self._company.setPlaceholderText("Назва організації")
        layout.addWidget(self._company)

        self._contact_person = QLineEdit()
        self._contact_person.setPlaceholderText("Відповідальна особа")
        layout.addWidget(self._contact_person)

        self._contact_phone = QLineEdit()
        self._contact_phone.setPlaceholderText("Телефон")
        layout.addWidget(self._contact_phone)

        self._contact_email = QLineEdit()
        self._contact_email.setPlaceholderText("Email")
        layout.addWidget(self._contact_email)

        self._status = QComboBox()
        self._status.addItem("Активний", "active")
        self._status.addItem("Завершений", "finished")
        self._status.addItem("Архівний", "archived")
        layout.addWidget(self._status)

        self._note = QTextEdit()
        self._note.setPlaceholderText("Примітка / зв'язок з допусками та роботами")
        self._note.setFixedHeight(120)
        layout.addWidget(self._note)

        self._save_button = QPushButton("Зберегти підрядника")
        self._save_button.setProperty("variant", "accent")
        self._save_button.clicked.connect(self._emit_save)
        layout.addWidget(self._save_button)

        self._new_button = QPushButton("Новий запис")
        self._new_button.setProperty("variant", "secondary")
        self._new_button.clicked.connect(self._reset_form)
        layout.addWidget(self._new_button)

        layout.addStretch()
        self._apply_read_only()

    # ###### РЕЖИМ READ-ONLY / READ-ONLY MODE ######
    def _apply_read_only(self) -> None:
        """Applies read-only restrictions."""

        editable = not self._read_only
        for widget in (self._company, self._contact_person, self._contact_phone, self._contact_email, self._status, self._note):
            widget.setEnabled(editable)
        self._save_button.setEnabled(editable)

    # ###### ПОКАЗ КАРТКИ ПІДРЯДНИКА / SHOW CONTRACTOR ######
    def show_record(self, record: ContractorRecord) -> None:
        """Displays selected contractor in form."""

        self._current_id = record.contractor_id
        self._company.setText(record.company_name)
        self._contact_person.setText(record.contact_person)
        self._contact_phone.setText(record.contact_phone)
        self._contact_email.setText(record.contact_email)
        status_index = self._status.findData(record.activity_status)
        self._status.setCurrentIndex(status_index if status_index >= 0 else 0)
        self._note.setPlainText(record.note_text)

    # ###### СКИДАННЯ ФОРМИ / RESET FORM ######
    def _reset_form(self) -> None:
        """Clears form for creating new contractor."""

        self._current_id = ""
        self._company.clear()
        self._contact_person.clear()
        self._contact_phone.clear()
        self._contact_email.clear()
        self._status.setCurrentIndex(0)
        self._note.clear()

    # ###### ЗБЕРЕЖЕННЯ КАРТКИ ПІДРЯДНИКА / SAVE CONTRACTOR CARD ######
    def _emit_save(self) -> None:
        """Emits contractor record save request."""

        self.save_requested.emit(
            ContractorRecord(
                contractor_id=self._current_id,
                company_name=self._company.text().strip(),
                contact_person=self._contact_person.text().strip(),
                contact_phone=self._contact_phone.text().strip(),
                contact_email=self._contact_email.text().strip(),
                activity_status=str(self._status.currentData() or "active"),
                note_text=self._note.toPlainText().strip(),
            )
        )
