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

from osah.application.services.create_employee import create_employee
from osah.domain.entities.employee_workspace import EmployeeWorkspace
from osah.ui.qt.components.form_feedback_label import FormFeedbackLabel
from osah.ui.qt.design.tokens import COLOR, SPACING


class CreateEmployeeDialog(QDialog):
    """Модальне вікно створення нового працівника.
    Modal dialog for creating a new employee.
    """

    employee_created = Signal(str)

    def __init__(self, database_path: Path, workspace: EmployeeWorkspace, parent=None) -> None:
        super().__init__(parent)
        self._database_path = database_path
        self._selected_photo_path: str | None = None
        self.setWindowTitle("Новий працівник")
        self.setModal(True)
        self.resize(520, 320)
        self.setStyleSheet(f"QDialog {{ background: {COLOR['bg_card']}; }}")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["lg"], SPACING["lg"], SPACING["lg"], SPACING["lg"])
        layout.setSpacing(SPACING["md"])

        form = QFormLayout()
        form.setSpacing(SPACING["sm"])

        self._personnel_number_input = QLineEdit()
        self._personnel_number_input.setPlaceholderText("Напр.: 0042")
        form.addRow("Табельний номер", self._personnel_number_input)

        self._full_name_input = QLineEdit()
        self._full_name_input.setPlaceholderText("ПІБ працівника")
        form.addRow("ПІБ", self._full_name_input)

        self._department_input = QComboBox()
        self._department_input.setEditable(True)
        self._department_input.addItem("", "")
        for department_name in sorted({row.department_name for row in workspace.rows}):
            self._department_input.addItem(department_name, department_name)
        self._department_input.setEditText("")
        self._department_input.setPlaceholderText("Виберіть або введіть підрозділ")
        form.addRow("Підрозділ", self._department_input)

        self._position_input = QComboBox()
        self._position_input.setEditable(True)
        self._position_input.addItem("", "")
        for position_name in sorted({row.position_name for row in workspace.rows}):
            self._position_input.addItem(position_name, position_name)
        self._position_input.setEditText("")
        self._position_input.setPlaceholderText("Виберіть або введіть посаду")
        form.addRow("Посада", self._position_input)

        self._status_input = QComboBox()
        self._status_input.addItem("Активний", "active")
        self._status_input.addItem("Архівний", "archived")
        self._status_input.addItem("Неактивний", "inactive")
        self._status_input.addItem("Звільнений", "dismissed")
        form.addRow("Статус", self._status_input)

        layout.addLayout(form)

        self._feedback_label = FormFeedbackLabel()
        layout.addWidget(self._feedback_label)

        photo_row = QHBoxLayout()
        self._photo_button = QPushButton("Додати фото")
        self._photo_button.setProperty("variant", "secondary")
        self._photo_button.clicked.connect(self._pick_photo)
        photo_row.addWidget(self._photo_button)

        self._photo_name_label = QLabel("Фото не вибрано")
        self._photo_name_label.setProperty("role", "status_muted")
        photo_row.addWidget(self._photo_name_label, stretch=1)
        layout.addLayout(photo_row)

        buttons_layout = QHBoxLayout()
        self._clear_button = QPushButton("Очистити")
        self._clear_button.setProperty("variant", "secondary")
        self._clear_button.clicked.connect(self._clear_form)
        buttons_layout.addWidget(self._clear_button)
        buttons_layout.addStretch()

        self._save_button = QPushButton("Зберегти")
        self._save_button.setProperty("variant", "accent")
        self._save_button.clicked.connect(self._save)
        buttons_layout.addWidget(self._save_button)
        layout.addLayout(buttons_layout)

    def _clear_form(self) -> None:
        self._personnel_number_input.clear()
        self._full_name_input.clear()
        self._department_input.setCurrentIndex(0)
        self._department_input.setEditText("")
        self._position_input.setCurrentIndex(0)
        self._position_input.setEditText("")
        self._status_input.setCurrentIndex(0)
        self._selected_photo_path = None
        self._photo_name_label.setText("Фото не вибрано")
        self._feedback_label.setVisible(False)

    def _save(self) -> None:
        try:
            create_employee(
                self._database_path,
                self._personnel_number_input.text(),
                self._full_name_input.text(),
                self._department_input.currentText(),
                self._position_input.currentText(),
                str(self._status_input.currentData()),
                self._selected_photo_path,
            )
        except ValueError as error:
            self._feedback_label.show_error(str(error))
            return

        self.employee_created.emit(self._personnel_number_input.text().strip())
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
        self._photo_name_label.setText(Path(photo_path).name)
