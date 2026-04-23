from PySide6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QLabel, QVBoxLayout

from osah.domain.entities.employee_workspace_row import EmployeeWorkspaceRow
from osah.ui.qt.design.tokens import COLOR, RADIUS, SPACING
from osah.ui.qt.screens.employees.employee_photo_widget import EmployeePhotoWidget
from osah.ui.qt.screens.employees.employee_row_state_badge import EmployeeRowStateBadge


class EmployeeHeaderCard(QFrame):
    """Шапка картки працівника з фото, даними і статусами.
    Employee card header with photo, identity data and statuses.
    """

    def __init__(self, row: EmployeeWorkspaceRow) -> None:
        super().__init__()
        self.setObjectName("employeeHeaderCard")
        self.setStyleSheet(
            f"QFrame#employeeHeaderCard {{ "
            f"background: {COLOR['bg_card']}; border: 1px solid {COLOR['border_soft']}; "
            f"border-radius: {RADIUS['xl']}px; "
            f"}}"
        )
        layout = QHBoxLayout(self)
        layout.setContentsMargins(SPACING["lg"], SPACING["lg"], SPACING["lg"], SPACING["lg"])
        layout.setSpacing(SPACING["lg"])

        layout.addWidget(EmployeePhotoWidget(row.photo_path, row.employee.full_name))

        info_layout = QVBoxLayout()
        info_layout.setSpacing(SPACING["sm"])
        name = QLabel(row.employee.full_name)
        name.setStyleSheet("font-size: 19px; font-weight: 900;")
        info_layout.addWidget(name)

        grid = QGridLayout()
        grid.setHorizontalSpacing(SPACING["lg"])
        grid.setVerticalSpacing(SPACING["xs"])
        _add_pair(grid, 0, "Табельний номер", row.employee.personnel_number)
        _add_pair(grid, 1, "Посада", row.position_name)
        _add_pair(grid, 2, "Підрозділ", row.department_name)
        _add_pair(grid, 3, "Участок", row.site_name)
        info_layout.addLayout(grid)
        layout.addLayout(info_layout, stretch=1)

        status_layout = QVBoxLayout()
        status_layout.setSpacing(SPACING["sm"])
        status_layout.addWidget(EmployeeRowStateBadge(row.status_level, row.status_label))
        reason = QLabel(row.status_reason)
        reason.setWordWrap(True)
        reason.setStyleSheet(f"color: {COLOR['text_secondary']};")
        status_layout.addWidget(reason)
        status_layout.addStretch()
        layout.addLayout(status_layout)


# ###### ПАРА ПОЛІВ ШАПКИ / HEADER FIELD PAIR ######
def _add_pair(grid: QGridLayout, row_index: int, title: str, value: str) -> None:
    """Додає одну пару 'назва-значення' в шапку картки.
    Adds one title-value pair into the card header.
    """

    title_label = QLabel(title)
    title_label.setStyleSheet(f"color: {COLOR['text_muted']}; font-weight: 700;")
    value_label = QLabel(value)
    value_label.setStyleSheet(f"color: {COLOR['text_primary']};")
    grid.addWidget(title_label, row_index, 0)
    grid.addWidget(value_label, row_index, 1)
