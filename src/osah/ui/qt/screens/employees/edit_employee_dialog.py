from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from osah.application.services.update_employee import update_employee
from osah.domain.entities.employee_workspace import EmployeeWorkspace
from osah.domain.entities.employee_workspace_row import EmployeeWorkspaceRow
from osah.ui.qt.components.form_feedback_label import FormFeedbackLabel
from osah.ui.qt.design.tokens import COLOR, SPACING


class EditEmployeeDialog(QDialog):
    """Модальне вікно редагування існуючого працівника.
    Modal dialog for editing an existing employee.
    """

    employee_updated = Signal(str)

    def __init__(self, database_path: Path, workspace: EmployeeWorkspace, row: EmployeeWorkspaceRow, parent=None) -> None:
        super().__init__(parent)
        self._database_path = database_path
        self._row = row
        self._selected_photo_path: str | None = None
        self._remove_photo = False

        self.setWindowTitle("Редагування працівника")
        self.setModal(True)
        self.resize(520, 340)
        self.setStyleSheet(f"QDialog {{ background: {COLOR['bg_card']}; }}")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["lg"], SPACING["lg"], SPACING["lg"], SPACING["lg"])
        layout.setSpacing(SPACING["md"])

        form = QFormLayout()
        form.setSpacing(SPACING["sm"])

        self._personnel_number_input = QLineEdit()
        self._personnel_number_input.setText(row.employee.personnel_number)
        self._personnel_number_input.setReadOnly(True)
        self._personnel_number_input.setStyleSheet("background-color: transparent; border: none; font-weight: bold;")
        form.addRow("Табельний номер", self._personnel_number_input)

        self._full_name_input = QLineEdit()
        self._full_name_input.setText(row.employee.full_name)
        form.addRow("ПІБ", self._full_name_input)

        self._department_input = QComboBox()
        self._department_input.setEditable(True)
        self._department_input.addItem("", "")
        for department_name in sorted({w_row.department_name for w_row in workspace.rows}):
            self._department_input.addItem(department_name, department_name)
        self._department_input.setEditText(row.department_name)
        form.addRow("Підрозділ", self._department_input)

        self._position_input = QComboBox()
        self._position_input.setEditable(True)
        self._position_input.addItem("", "")
        for position_name in sorted({w_row.position_name for w_row in workspace.rows}):
            self._position_input.addItem(position_name, position_name)
        self._position_input.setEditText(row.position_name)
        form.addRow("Посада", self._position_input)

        self._status_input = QComboBox()
        self._status_input.addItem("Активний", "active")
        self._status_input.addItem("Архівний", "archived")
        self._status_input.addItem("Неактивний", "inactive")
        self._status_input.addItem("Звільнений", "dismissed")
        
        # Set current status
        index = self._status_input.findData(row.employee.employment_status)
        if index >= 0:
            self._status_input.setCurrentIndex(index)
            
        form.addRow("Статус", self._status_input)

        layout.addLayout(form)

        self._feedback_label = FormFeedbackLabel()
        layout.addWidget(self._feedback_label)

        photo_row = QHBoxLayout()
        self._photo_button = QPushButton("Змінити фото")
        self._photo_button.setProperty("variant", "secondary")
        self._photo_button.clicked.connect(self._pick_photo)
        photo_row.addWidget(self._photo_button)

        self._remove_photo_button = QPushButton("Видалити фото")
        self._remove_photo_button.setProperty("variant", "secondary")
        self._remove_photo_button.setStyleSheet("color: #d32f2f;")
        self._remove_photo_button.clicked.connect(self._on_remove_photo_clicked)
        photo_row.addWidget(self._remove_photo_button)

        self._photo_name_label = QLabel("Фото не змінено" if row.employee.photo_path else "Фото відсутнє")
        self._photo_name_label.setProperty("role", "status_muted")
        photo_row.addWidget(self._photo_name_label, stretch=1)
        layout.addLayout(photo_row)

        buttons_layout = QHBoxLayout()
        self._cancel_button = QPushButton("Скасувати")
        self._cancel_button.setProperty("variant", "secondary")
        self._cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self._cancel_button)
        buttons_layout.addStretch()

        self._save_button = QPushButton("Зберегти")
        self._save_button.setProperty("variant", "accent")
        self._save_button.clicked.connect(self._save)
        buttons_layout.addWidget(self._save_button)
        layout.addLayout(buttons_layout)

    def _on_remove_photo_clicked(self) -> None:
        self._remove_photo = True
        self._selected_photo_path = None
        self._photo_name_label.setText("Фото буде видалено")

    def _save(self) -> None:
        try:
            update_employee(
                self._database_path,
                self._personnel_number_input.text(),
                self._full_name_input.text(),
                self._department_input.currentText(),
                self._position_input.currentText(),
                str(self._status_input.currentData()),
                self._selected_photo_path,
                self._remove_photo,
            )
        except ValueError as error:
            self._feedback_label.show_error(str(error))
            return

        self.employee_updated.emit(self._personnel_number_input.text().strip())
        self.accept()

    def _pick_photo(self) -> None:
        photo_path, _ = QFileDialog.getOpenFileName(
            self,
            "Виберіть фото працівника",
            "",
            "Image Files (*.png *.jpg *.jpeg *.webp *.bmp)",
        )
        if not photo_path:
            return
        self._selected_photo_path = photo_path
        self._remove_photo = False
        self._photo_name_label.setText(Path(photo_path).name)
