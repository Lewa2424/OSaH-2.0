from PySide6.QtCore import Signal
from PySide6.QtGui import QMouseEvent, Qt
from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QVBoxLayout, QWidget

from osah.domain.entities.app_section import AppSection
from osah.domain.entities.employee_module_status_summary import EmployeeModuleStatusSummary
from osah.domain.entities.employee_workspace_row import EmployeeWorkspaceRow
from osah.ui.qt.design.tokens import COLOR, RADIUS, SPACING
from osah.ui.qt.screens.employees.employee_problem_summary import EmployeeProblemSummary
from osah.ui.qt.screens.employees.employee_row_state_badge import EmployeeRowStateBadge


def _map_module_name_to_section(name: str) -> AppSection | None:
    """Мапує локалізовану назву модуля на AppSection."""
    name_lower = name.lower()
    if "інструктаж" in name_lower:
        return AppSection.TRAININGS
    if "зіз" in name_lower:
        return AppSection.PPE
    if "медицин" in name_lower:
        return AppSection.MEDICAL
    if "наряд" in name_lower:
        return AppSection.WORK_PERMITS
    return None


class EmployeeOverviewTab(QWidget):
    """Вкладка огляду ОП-стану працівника.
    Overview tab for an employee safety state.
    """

    module_clicked = Signal(AppSection)

    def __init__(self, row: EmployeeWorkspaceRow) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["lg"], SPACING["lg"], SPACING["lg"], SPACING["lg"])
        layout.setSpacing(SPACING["lg"])

        answer = QLabel(f"Чи можна працювати: {row.status_label}. Причина: {row.status_reason}.")
        answer.setWordWrap(True)
        answer.setStyleSheet("font-size: 14px; font-weight: 800;")
        layout.addWidget(answer)

        layout.addWidget(EmployeeProblemSummary(row.problems))

        grid = QGridLayout()
        grid.setSpacing(SPACING["md"])
        for index, summary in enumerate(row.module_summaries):
            card = _ModuleSummaryCard(summary)
            card.clicked.connect(self.module_clicked.emit)
            grid.addWidget(card, index // 2, index % 2)
        layout.addLayout(grid)
        layout.addStretch()


class _ModuleSummaryCard(QFrame):
    clicked = Signal(AppSection)

    def __init__(self, summary: EmployeeModuleStatusSummary) -> None:
        """Створює картку короткого стану одного ОП-модуля.
        Creates a compact status card for one safety module.
        """

        super().__init__()
        self.setObjectName("employeeModuleSummaryCard")
        self._target_section = _map_module_name_to_section(summary.module_name)
        if self._target_section:
            self.setCursor(Qt.CursorShape.PointingHandCursor)

        self.setStyleSheet(
            f"QFrame#employeeModuleSummaryCard {{ "
            f"background: {COLOR['bg_card']}; border: 1px solid {COLOR['border_soft']}; "
            f"border-radius: {RADIUS['lg']}px; "
            f"}}"
            f"QFrame#employeeModuleSummaryCard:hover {{ "
            f"border: 1px solid {COLOR['accent']}; background: #f8f9fa; "
            f"}}"
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["md"], SPACING["md"], SPACING["md"], SPACING["md"])
        layout.setSpacing(SPACING["sm"])

        title = QLabel(summary.module_name)
        title.setStyleSheet("font-size: 12px; font-weight: 800;")
        layout.addWidget(title)
        layout.addWidget(EmployeeRowStateBadge(summary.level, summary.label))
        reason = QLabel(summary.reason)
        reason.setWordWrap(True)
        reason.setStyleSheet(f"color: {COLOR['text_secondary']};")
        layout.addWidget(reason)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton and self._target_section:
            self.clicked.emit(self._target_section)
        super().mousePressEvent(event)
