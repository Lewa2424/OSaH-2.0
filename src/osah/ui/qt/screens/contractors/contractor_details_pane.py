from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from osah.domain.entities.contractor_readiness_snapshot import ContractorReadinessSnapshot
from osah.domain.entities.contractor_record import ContractorRecord
from osah.domain.entities.contractor_worker import ContractorWorker
from osah.ui.qt.components.app_dialog import show_app_confirm_dialog


class ContractorDetailsPane(QWidget):
    """Легка картка підрядника з контролем складу і готовності.
    Lightweight contractor card with crew and readiness control.
    """

    save_requested = Signal(object)
    delete_requested = Signal(str)

    def __init__(self, read_only: bool) -> None:
        super().__init__()
        self._read_only = read_only
        self._current_id = ""

        layout = QVBoxLayout(self)

        title = QLabel("Картка підрядника")
        title.setProperty("role", "section_title")
        layout.addWidget(title)

        self._status_label = QLabel("Статус: -")
        self._headline_label = QLabel("Оберіть підрядника або створіть новий запис.")
        self._headline_label.setWordWrap(True)
        self._issues_label = QLabel("Проблеми: -")
        self._issues_label.setWordWrap(True)
        layout.addWidget(self._status_label)
        layout.addWidget(self._headline_label)
        layout.addWidget(self._issues_label)

        contacts_box = QGroupBox("Організація та відповідальні")
        contacts_layout = QGridLayout(contacts_box)
        self._company = QLineEdit()
        self._contact_person = QLineEdit()
        self._contact_phone = QLineEdit()
        self._contact_email = QLineEdit()
        self._enterprise_supervisor = QLineEdit()
        self._status = QComboBox()
        self._status.addItem("Активний", "active")
        self._status.addItem("Завершений", "finished")
        self._status.addItem("Архівний", "archived")

        contacts_layout.addWidget(QLabel("Організація"), 0, 0)
        contacts_layout.addWidget(self._company, 0, 1)
        contacts_layout.addWidget(QLabel("Контакт підрядника"), 1, 0)
        contacts_layout.addWidget(self._contact_person, 1, 1)
        contacts_layout.addWidget(QLabel("Телефон"), 2, 0)
        contacts_layout.addWidget(self._contact_phone, 2, 1)
        contacts_layout.addWidget(QLabel("Email"), 3, 0)
        contacts_layout.addWidget(self._contact_email, 3, 1)
        contacts_layout.addWidget(QLabel("Відповідальний від підприємства"), 4, 0)
        contacts_layout.addWidget(self._enterprise_supervisor, 4, 1)
        contacts_layout.addWidget(QLabel("Режим співпраці"), 5, 0)
        contacts_layout.addWidget(self._status, 5, 1)
        layout.addWidget(contacts_box)

        self._work_scope = QTextEdit()
        self._work_scope.setPlaceholderText("Де та які роботи виконує підрядник зараз.")
        self._work_scope.setFixedHeight(80)
        layout.addWidget(QLabel("Поточні роботи / зона допуску"))
        layout.addWidget(self._work_scope)

        layout.addWidget(QLabel("Склад працівників підрядника"))
        self._workers_table = QTableWidget(0, 7)
        self._workers_table.setHorizontalHeaderLabels(
            ["ПІБ", "Роль", "Інстр.", "ЗІЗ", "Мед.", "Допуск", "Примітка"]
        )
        self._workers_table.verticalHeader().setDefaultSectionSize(34)
        self._workers_table.setMinimumHeight(180)
        self._workers_table.setColumnWidth(0, 170)
        self._workers_table.setColumnWidth(1, 130)
        self._workers_table.setColumnWidth(2, 72)
        self._workers_table.setColumnWidth(3, 72)
        self._workers_table.setColumnWidth(4, 72)
        self._workers_table.setColumnWidth(5, 72)
        self._workers_table.setColumnWidth(6, 220)
        self._workers_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self._workers_table)

        workers_actions = QHBoxLayout()
        self._add_worker_button = QPushButton("Додати працівника")
        self._add_worker_button.setProperty("variant", "secondary")
        self._add_worker_button.clicked.connect(self._add_worker_row)
        workers_actions.addWidget(self._add_worker_button)
        self._remove_worker_button = QPushButton("Вилучити працівника")
        self._remove_worker_button.setProperty("variant", "secondary")
        self._remove_worker_button.clicked.connect(self._remove_selected_worker)
        workers_actions.addWidget(self._remove_worker_button)
        layout.addLayout(workers_actions)

        self._note = QTextEdit()
        self._note.setPlaceholderText("Службові примітки щодо допуску або організації робіт.")
        self._note.setFixedHeight(100)
        layout.addWidget(QLabel("Примітка"))
        layout.addWidget(self._note)

        actions = QHBoxLayout()
        self._save_button = QPushButton("Зберегти підрядника")
        self._save_button.setProperty("variant", "accent")
        self._save_button.clicked.connect(self._emit_save)
        actions.addWidget(self._save_button)
        self._new_button = QPushButton("Новий запис")
        self._new_button.setProperty("variant", "secondary")
        self._new_button.clicked.connect(self._reset_form)
        actions.addWidget(self._new_button)
        self._delete_button = QPushButton("Видалити підрядника")
        self._delete_button.setProperty("variant", "secondary")
        self._delete_button.clicked.connect(self._emit_delete)
        actions.addWidget(self._delete_button)
        layout.addLayout(actions)

        layout.addStretch()
        self._apply_read_only()

    def _apply_read_only(self) -> None:
        """Застосовує обмеження read-only до картки підрядника.
        Applies read-only restrictions to contractor card.
        """

        editable = not self._read_only
        for widget in (
            self._company,
            self._contact_person,
            self._contact_phone,
            self._contact_email,
            self._enterprise_supervisor,
            self._status,
            self._work_scope,
            self._workers_table,
            self._note,
        ):
            widget.setEnabled(editable)
        self._save_button.setEnabled(editable)
        self._add_worker_button.setEnabled(editable)
        self._remove_worker_button.setEnabled(editable)
        self._delete_button.setEnabled(editable)

    def show_record(self, record: ContractorRecord, readiness: ContractorReadinessSnapshot) -> None:
        """Показує вибраного підрядника та поточний стан його готовності.
        Displays selected contractor and current readiness state.
        """

        self._current_id = record.contractor_id
        self._company.setText(record.company_name)
        self._contact_person.setText(record.contact_person)
        self._contact_phone.setText(record.contact_phone)
        self._contact_email.setText(record.contact_email)
        self._enterprise_supervisor.setText(record.enterprise_supervisor)
        self._work_scope.setPlainText(record.work_scope_text)
        self._note.setPlainText(record.note_text)
        self._status_label.setText(f"Статус: {readiness.status_label}")
        self._headline_label.setText(readiness.headline_text)
        self._issues_label.setText(f"Проблеми: {readiness.issues_text}")
        status_index = self._status.findData(record.activity_status)
        self._status.setCurrentIndex(status_index if status_index >= 0 else 0)
        self._set_workers(record.workers)

    def _set_workers(self, workers: tuple[ContractorWorker, ...]) -> None:
        self._workers_table.setRowCount(0)
        for worker in workers:
            self._append_worker_row(worker)
        self._workers_table.resizeRowsToContents()

    def _append_worker_row(self, worker: ContractorWorker | None = None) -> None:
        row_index = self._workers_table.rowCount()
        self._workers_table.insertRow(row_index)
        self._workers_table.setItem(row_index, 0, QTableWidgetItem(worker.full_name if worker else ""))
        self._workers_table.setItem(row_index, 1, QTableWidgetItem(worker.role_name if worker else ""))
        self._workers_table.setCellWidget(row_index, 2, self._build_bool_checkbox(worker.training_ok if worker else False))
        self._workers_table.setCellWidget(row_index, 3, self._build_bool_checkbox(worker.ppe_ok if worker else False))
        self._workers_table.setCellWidget(row_index, 4, self._build_bool_checkbox(worker.medical_ok if worker else False))
        self._workers_table.setCellWidget(row_index, 5, self._build_bool_checkbox(worker.access_ok if worker else False))
        self._workers_table.setItem(row_index, 6, QTableWidgetItem(worker.note_text if worker else ""))

    def _build_bool_checkbox(self, value: bool) -> QWidget:
        checkbox = QCheckBox()
        checkbox.setChecked(value)
        checkbox.setEnabled(not self._read_only)
        checkbox.setFixedSize(22, 22)
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addStretch()
        layout.addWidget(checkbox)
        layout.addStretch()
        return container

    def _add_worker_row(self) -> None:
        """Додає порожній рядок працівника підрядника.
        Adds an empty contractor worker row.
        """

        self._append_worker_row()
        self._workers_table.resizeRowsToContents()

    def _remove_selected_worker(self) -> None:
        """Видаляє вибраний рядок працівника зі складу.
        Removes selected worker row from contractor crew.
        """

        selected_rows = self._workers_table.selectionModel().selectedRows()
        if not selected_rows:
            return
        self._workers_table.removeRow(selected_rows[0].row())
        self._workers_table.resizeRowsToContents()

    def _reset_form(self) -> None:
        """Очищує картку для створення нового підрядника.
        Clears the card for creating a new contractor.
        """

        self._current_id = ""
        self._company.clear()
        self._contact_person.clear()
        self._contact_phone.clear()
        self._contact_email.clear()
        self._enterprise_supervisor.clear()
        self._work_scope.clear()
        self._status.setCurrentIndex(0)
        self._note.clear()
        self._workers_table.setRowCount(0)
        self._status_label.setText("Статус: -")
        self._headline_label.setText("Створіть підрядника та задайте склад людей для контролю готовності.")
        self._issues_label.setText("Проблеми: -")

    def _emit_save(self) -> None:
        """Формує запис підрядника з поточних полів форми.
        Builds contractor record from current form fields.
        """

        workers: list[ContractorWorker] = []
        for row_index in range(self._workers_table.rowCount()):
            full_name_item = self._workers_table.item(row_index, 0)
            role_item = self._workers_table.item(row_index, 1)
            note_item = self._workers_table.item(row_index, 6)
            full_name = full_name_item.text().strip() if full_name_item else ""
            if not full_name:
                continue
            role_name = role_item.text().strip() if role_item else ""
            note_text = note_item.text().strip() if note_item else ""
            workers.append(
                ContractorWorker(
                    worker_id=f"{self._current_id or 'new'}-{row_index + 1}",
                    full_name=full_name,
                    role_name=role_name,
                    training_ok=self._bool_cell_value(row_index, 2),
                    ppe_ok=self._bool_cell_value(row_index, 3),
                    medical_ok=self._bool_cell_value(row_index, 4),
                    access_ok=self._bool_cell_value(row_index, 5),
                    note_text=note_text,
                )
            )

        self.save_requested.emit(
            ContractorRecord(
                contractor_id=self._current_id,
                company_name=self._company.text().strip(),
                contact_person=self._contact_person.text().strip(),
                contact_phone=self._contact_phone.text().strip(),
                contact_email=self._contact_email.text().strip(),
                activity_status=str(self._status.currentData() or "active"),
                note_text=self._note.toPlainText().strip(),
                enterprise_supervisor=self._enterprise_supervisor.text().strip(),
                work_scope_text=self._work_scope.toPlainText().strip(),
                workers=tuple(workers),
            )
        )

    def _emit_delete(self) -> None:
        """Запитує підтвердження і передає назовні видалення підрядника.
        Asks for confirmation and emits contractor deletion request.
        """

        if not self._current_id:
            return
        contractor_name = self._company.text().strip()
        detail_lines = ["Дію буде зафіксовано в журналі аудиту."]
        if contractor_name:
            detail_lines.insert(0, f"Організація: {contractor_name}")
        if not show_app_confirm_dialog(
            self,
            "Видалити підрядника",
            "Видалити поточний запис підрядника з реєстру?",
            detail="\n".join(detail_lines),
            confirm_label="Видалити",
            destructive=True,
        ):
            return
        self.delete_requested.emit(self._current_id)

    def _bool_cell_value(self, row_index: int, column_index: int) -> bool:
        container = self._workers_table.cellWidget(row_index, column_index)
        if isinstance(container, QWidget):
            checkbox = container.findChild(QCheckBox)
            if isinstance(checkbox, QCheckBox):
                return checkbox.isChecked()
        return False
