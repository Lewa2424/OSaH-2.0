from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from osah.application.services.create_employee import create_employee
from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.employee_workspace import EmployeeWorkspace
from osah.ui.qt.components.form_feedback_label import FormFeedbackLabel
from osah.ui.qt.design.tokens import COLOR, RADIUS, SPACING


class CreateEmployeeDialog(QDialog):
    """Modal dialog for creating a new employee. / Модальне вікно створення нового працівника."""

    employee_created = Signal(str)

    def __init__(self, database_path: Path, workspace: EmployeeWorkspace, access_role: AccessRole, parent=None) -> None:
        super().__init__(parent)
        self._database_path = database_path
        self._access_role = access_role
        self._selected_photo_path: str | None = None

        self.setWindowTitle("Новий працівник")
        self.setModal(True)
        self.resize(640, 520)
        self.setStyleSheet(
            f"""
            QDialog {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #F9FBFD, stop:0.55 #F2F6FB, stop:1 #EEF4F9);
            }}
            QFrame#dialogSurface {{
                background: rgba(255, 255, 255, 0.96);
                border: 1px solid #D9E2EC;
                border-radius: {RADIUS['xxl']}px;
            }}
            QLabel#dialogEyebrow {{
                color: {COLOR['accent']};
                font-size: 13px;
                font-weight: 900;
                letter-spacing: 0.6px;
            }}
            QLabel#dialogTitle {{
                color: {COLOR['text_primary']};
                font-size: 24px;
                font-weight: 900;
            }}
            QLabel#dialogSubtitle {{
                color: {COLOR['text_secondary']};
                font-size: 14px;
                font-weight: 600;
            }}
            QLabel#fieldHint {{
                color: {COLOR['text_muted']};
                font-size: 13px;
                font-weight: 700;
            }}
            QLabel {{
                color: {COLOR['text_primary']};
            }}
            QLineEdit, QComboBox {{
                min-height: 42px;
                padding: 0 14px;
                background: #FFFFFF;
                color: {COLOR['text_primary']};
                border: 1px solid #C9D4DF;
                border-radius: {RADIUS['lg']}px;
                font-size: 14px;
                font-weight: 600;
            }}
            QLineEdit:focus, QComboBox:focus {{
                border: 1px solid {COLOR['accent']};
                background: #FCFEFF;
            }}
            QComboBox::drop-down {{
                width: 34px;
                border: none;
                background: transparent;
            }}
            QComboBox QAbstractItemView {{
                background: #FFFFFF;
                color: {COLOR['text_primary']};
                border: 1px solid #D9E2EC;
                border-radius: {RADIUS['md']}px;
                padding: 6px;
                selection-background-color: #EAF1F8;
                selection-color: {COLOR['text_primary']};
                outline: none;
            }}
            QPushButton {{
                min-height: 42px;
                padding: 0 18px;
                border-radius: {RADIUS['lg']}px;
                font-size: 14px;
                font-weight: 800;
            }}
            """
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(SPACING["xl"], SPACING["xl"], SPACING["xl"], SPACING["xl"])
        root.setSpacing(0)

        surface = QFrame()
        surface.setObjectName("dialogSurface")
        root.addWidget(surface)

        layout = QVBoxLayout(surface)
        layout.setContentsMargins(SPACING["xl"], SPACING["xl"], SPACING["xl"], SPACING["xl"])
        layout.setSpacing(SPACING["lg"])

        layout.addWidget(self._build_header())

        form = QFormLayout()
        form.setContentsMargins(0, 0, 0, 0)
        form.setHorizontalSpacing(SPACING["lg"])
        form.setVerticalSpacing(SPACING["md"])
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        self._personnel_number_input = QLineEdit()
        self._personnel_number_input.setPlaceholderText("Напр.: 0042")
        form.addRow(_build_form_label("Табельний номер"), self._personnel_number_input)

        self._full_name_input = QLineEdit()
        self._full_name_input.setPlaceholderText("ПІБ працівника")
        form.addRow(_build_form_label("ПІБ"), self._full_name_input)

        self._department_input = QComboBox()
        self._department_input.setEditable(True)
        self._department_input.addItem("", "")
        for department_name in sorted({row.department_name for row in workspace.rows}):
            self._department_input.addItem(department_name, department_name)
        self._department_input.setEditText("")
        self._department_input.setPlaceholderText("Виберіть або введіть підрозділ")
        form.addRow(_build_form_label("Підрозділ"), self._department_input)

        self._position_input = QComboBox()
        self._position_input.setEditable(True)
        self._position_input.addItem("", "")
        for position_name in sorted({row.position_name for row in workspace.rows}):
            self._position_input.addItem(position_name, position_name)
        self._position_input.setEditText("")
        self._position_input.setPlaceholderText("Виберіть або введіть посаду")
        form.addRow(_build_form_label("Посада"), self._position_input)

        self._status_input = QComboBox()
        self._status_input.addItem("Активний", "active")
        self._status_input.addItem("Архівний", "archived")
        self._status_input.addItem("Неактивний", "inactive")
        self._status_input.addItem("Звільнений", "dismissed")
        form.addRow(_build_form_label("Статус"), self._status_input)

        layout.addLayout(form)

        self._feedback_label = FormFeedbackLabel()
        layout.addWidget(self._feedback_label)

        layout.addWidget(self._build_photo_card())
        layout.addLayout(self._build_actions())

    def _build_header(self) -> QWidget:
        header = QWidget()
        layout = QVBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING["xs"])

        eyebrow = QLabel("КАРТКА ПРАЦІВНИКА")
        eyebrow.setObjectName("dialogEyebrow")
        layout.addWidget(eyebrow)

        title = QLabel("Новий працівник")
        title.setObjectName("dialogTitle")
        layout.addWidget(title)

        subtitle = QLabel("Заповніть ключові кадрові поля та, за потреби, додайте фото працівника.")
        subtitle.setObjectName("dialogSubtitle")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)
        return header

    def _build_photo_card(self) -> QWidget:
        card = QFrame()
        card.setStyleSheet(
            f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #F7FAFD, stop:1 #F1F6FB);
                border: 1px solid #D9E2EC;
                border-radius: {RADIUS['xl']}px;
            }}
            """
        )
        layout = QVBoxLayout(card)
        layout.setContentsMargins(SPACING["lg"], SPACING["md"], SPACING["lg"], SPACING["md"])
        layout.setSpacing(SPACING["sm"])

        hint = QLabel("Фото працівника")
        hint.setObjectName("fieldHint")
        layout.addWidget(hint)

        row = QHBoxLayout()
        row.setSpacing(SPACING["sm"])

        self._photo_button = QPushButton("Додати фото")
        self._photo_button.setProperty("variant", "secondary")
        self._photo_button.clicked.connect(self._pick_photo)
        row.addWidget(self._photo_button)

        self._photo_name_label = QLabel("Фото не вибрано")
        self._photo_name_label.setObjectName("fieldHint")
        row.addWidget(self._photo_name_label, stretch=1)

        layout.addLayout(row)
        return card

    def _build_actions(self) -> QHBoxLayout:
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(SPACING["sm"])

        self._clear_button = QPushButton("Очистити")
        self._clear_button.setProperty("variant", "secondary")
        self._clear_button.clicked.connect(self._clear_form)
        buttons_layout.addWidget(self._clear_button)
        buttons_layout.addStretch()

        self._save_button = QPushButton("Зберегти")
        self._save_button.setProperty("variant", "accent")
        self._save_button.clicked.connect(self._save)
        buttons_layout.addWidget(self._save_button)
        return buttons_layout

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
                access_role=self._access_role,
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


def _build_form_label(text: str) -> QLabel:
    label = QLabel(text)
    label.setStyleSheet(
        f"color: {COLOR['text_secondary']}; font-size: 13px; font-weight: 800; padding-bottom: 2px;"
    )
    return label
