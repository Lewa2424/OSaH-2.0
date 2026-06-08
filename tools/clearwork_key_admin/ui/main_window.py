from pathlib import Path

from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from services.ensure_registry_schema import ensure_registry_schema
from services.generate_setup_key_for_customer import generate_setup_key_for_customer
from services.insert_key_issue_record import KeyIssueRecordInput, insert_key_issue_record
from services.list_key_issue_records import KeyIssueRecordRow, list_key_issue_records


class KeyAdminMainWindow(QMainWindow):
    """Головне вікно обліку ключів установки ClearWork."""

    def __init__(self, project_root: Path) -> None:
        super().__init__()
        self._project_root = project_root
        self._database_path = project_root / "data" / "registry.sqlite3"
        self._private_key_path = project_root / "keys" / "private_key.pem"
        self._generated_token = ""
        ensure_registry_schema(self._database_path)
        self.setWindowTitle("ClearWork Key Admin")
        self.resize(1180, 760)
        self._build_ui()
        self._reload_table()

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title = QLabel("Облік ключів установки ClearWork")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        layout.addWidget(title)

        form_card = QWidget()
        form_layout = QFormLayout(form_card)
        form_layout.setSpacing(10)

        self._customer_input = QLineEdit()
        self._contact_input = QLineEdit()
        self._installation_id_input = QLineEdit()
        self._key_kind_input = QComboBox()
        self._key_kind_input.addItems(["initial", "rebind"])
        self._previous_record_input = QLineEdit()
        self._previous_record_input.setPlaceholderText("ID попереднього запису (для rebind)")
        self._note_input = QPlainTextEdit()
        self._note_input.setMaximumHeight(80)

        form_layout.addRow("Підприємство", self._customer_input)
        form_layout.addRow("Контакт", self._contact_input)
        form_layout.addRow("ID установки", self._installation_id_input)
        form_layout.addRow("Тип ключа", self._key_kind_input)
        form_layout.addRow("Попередній запис", self._previous_record_input)
        form_layout.addRow("Примітка", self._note_input)
        layout.addWidget(form_card)

        button_row = QHBoxLayout()
        generate_button = QPushButton("Згенерувати ключ")
        generate_button.clicked.connect(self._on_generate_clicked)
        copy_button = QPushButton("Копіювати ключ")
        copy_button.clicked.connect(self._on_copy_clicked)
        refresh_button = QPushButton("Оновити список")
        refresh_button.clicked.connect(self._reload_table)
        button_row.addWidget(generate_button)
        button_row.addWidget(copy_button)
        button_row.addWidget(refresh_button)
        button_row.addStretch()
        layout.addLayout(button_row)

        self._token_output = QPlainTextEdit()
        self._token_output.setReadOnly(True)
        self._token_output.setPlaceholderText("Тут з'явиться згенерований ключ CW-...")
        self._token_output.setMaximumHeight(90)
        layout.addWidget(self._token_output)

        self._table = QTableWidget(0, 8)
        self._table.setHorizontalHeaderLabels(
            [
                "ID",
                "Дата",
                "Підприємство",
                "Контакт",
                "ID установки",
                "Тип",
                "Попередній",
                "Примітка",
            ]
        )
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.cellDoubleClicked.connect(self._on_row_double_clicked)
        layout.addWidget(self._table)

    def _on_generate_clicked(self) -> None:
        customer = self._customer_input.text().strip()
        installation_id = self._installation_id_input.text().strip()
        if not customer or not installation_id:
            QMessageBox.warning(self, "ClearWork Key Admin", "Заповніть підприємство та ID установки.")
            return
        if not self._private_key_path.is_file():
            QMessageBox.critical(
                self,
                "ClearWork Key Admin",
                f"Не знайдено private_key.pem:\n{self._private_key_path}",
            )
            return

        key_kind = self._key_kind_input.currentText()
        previous_record_text = self._previous_record_input.text().strip()
        previous_record_id = int(previous_record_text) if previous_record_text else None

        try:
            paste_token = generate_setup_key_for_customer(
                customer=customer,
                installation_id=installation_id,
                key_kind=key_kind,  # type: ignore[arg-type]
                private_key_path=self._private_key_path,
            )
        except Exception as error:
            QMessageBox.critical(self, "ClearWork Key Admin", f"Не вдалося згенерувати ключ:\n{error}")
            return

        record_id = insert_key_issue_record(
            self._database_path,
            KeyIssueRecordInput(
                customer=customer,
                contact=self._contact_input.text(),
                installation_id=installation_id,
                key_kind=key_kind,
                previous_record_id=previous_record_id,
                note=self._note_input.toPlainText(),
                paste_token=paste_token,
            ),
        )
        self._generated_token = paste_token
        self._token_output.setPlainText(paste_token)
        self._reload_table()
        QMessageBox.information(
            self,
            "ClearWork Key Admin",
            f"Ключ згенеровано та збережено (запис #{record_id}).",
        )

    def _on_copy_clicked(self) -> None:
        token_text = self._token_output.toPlainText().strip()
        if not token_text:
            QMessageBox.warning(self, "ClearWork Key Admin", "Немає ключа для копіювання.")
            return
        self.clipboard().setText(token_text)
        QMessageBox.information(self, "ClearWork Key Admin", "Ключ скопійовано в буфер обміну.")

    def _reload_table(self) -> None:
        records = list_key_issue_records(self._database_path)
        self._table.setRowCount(len(records))
        for row_index, record in enumerate(records):
            self._fill_row(row_index, record)
        self._table.resizeColumnsToContents()

    def _fill_row(self, row_index: int, record: KeyIssueRecordRow) -> None:
        values = [
            str(record.record_id),
            record.created_at,
            record.customer,
            record.contact,
            record.installation_id,
            record.key_kind,
            "" if record.previous_record_id is None else str(record.previous_record_id),
            record.note,
        ]
        for column_index, value in enumerate(values):
            self._table.setItem(row_index, column_index, QTableWidgetItem(value))

    def _on_row_double_clicked(self, row_index: int, _column_index: int) -> None:
        token_item = list_key_issue_records(self._database_path)
        if row_index < 0 or row_index >= len(token_item):
            return
        selected = token_item[row_index]
        self._token_output.setPlainText(selected.paste_token)
        self._customer_input.setText(selected.customer)
        self._contact_input.setText(selected.contact)
        self._installation_id_input.setText(selected.installation_id)
        self._key_kind_input.setCurrentText(selected.key_kind)
        self._previous_record_input.setText(
            "" if selected.previous_record_id is None else str(selected.previous_record_id)
        )
        self._note_input.setPlainText(selected.note)
