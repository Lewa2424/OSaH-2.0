from PySide6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QLabel, QVBoxLayout

from osah.domain.entities.employee_workspace_row import EmployeeWorkspaceRow
from osah.ui.qt.design.tokens import COLOR, RADIUS, SPACING
from osah.ui.qt.screens.employees.employee_photo_widget import EmployeePhotoWidget


class EmployeeHeaderCard(QFrame):
    """Employee card header with photo and identity data. / Шапка карточки работника с фото и идентификацией."""

    def __init__(self, row: EmployeeWorkspaceRow) -> None:
        super().__init__()
        self.setObjectName("employeeHeaderCard")
        self.setStyleSheet(
            f"""
            QFrame#employeeHeaderCard {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #FFFFFF, stop:0.55 #F7FAFD, stop:1 #ECF3FA);
                border: 1px solid {COLOR['border_soft']};
                border-radius: {RADIUS['xxl']}px;
            }}
            QLabel#employeeHeaderName {{
                color: {COLOR['text_primary']};
                font-size: 22px;
                font-weight: 900;
            }}
            QLabel[role="employeeHeaderTitle"] {{
                color: {COLOR['text_muted']};
                font-size: 13px;
                font-weight: 800;
            }}
            QLabel[role="employeeHeaderValue"] {{
                color: {COLOR['text_primary']};
                font-size: 15px;
                font-weight: 700;
            }}
            """
        )
        layout = QHBoxLayout(self)
        layout.setContentsMargins(SPACING["lg"], SPACING["lg"], SPACING["lg"], SPACING["lg"])
        layout.setSpacing(SPACING["lg"])

        layout.addWidget(EmployeePhotoWidget(row.photo_path, row.employee.full_name))

        info_layout = QVBoxLayout()
        info_layout.setSpacing(SPACING["sm"])

        name = QLabel(row.employee.full_name)
        name.setObjectName("employeeHeaderName")
        info_layout.addWidget(name)

        grid = QGridLayout()
        grid.setHorizontalSpacing(SPACING["xl"])
        grid.setVerticalSpacing(SPACING["xs"])
        _add_pair(grid, 0, "Табельний номер", row.employee.personnel_number)
        _add_pair(grid, 1, "Посада", row.position_name)
        _add_pair(grid, 2, "Підрозділ", row.department_name)
        _add_pair(grid, 3, "Участок", row.site_name)
        info_layout.addLayout(grid)
        layout.addLayout(info_layout, stretch=1)


def _add_pair(grid: QGridLayout, row_index: int, title: str, value: str) -> None:
    """Adds title/value pair to the header. / Добавляет пару заголовок/значение в шапку."""

    title_label = QLabel(title)
    title_label.setProperty("role", "employeeHeaderTitle")
    value_label = QLabel(value)
    value_label.setProperty("role", "employeeHeaderValue")
    grid.addWidget(title_label, row_index, 0)
    grid.addWidget(value_label, row_index, 1)
