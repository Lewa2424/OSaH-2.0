from PySide6.QtCore import Signal
from PySide6.QtGui import QMouseEvent, Qt
from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QVBoxLayout, QWidget

from osah.domain.entities.app_section import AppSection
from osah.domain.entities.employee_module_status_summary import EmployeeModuleStatusSummary
from osah.domain.entities.employee_status_level import EmployeeStatusLevel
from osah.domain.entities.employee_workspace_row import EmployeeWorkspaceRow
from osah.ui.qt.design.tokens import COLOR, RADIUS, SPACING
from osah.ui.qt.screens.employees.employee_problem_summary import EmployeeProblemSummary
from osah.ui.qt.screens.employees.employee_row_state_badge import EmployeeRowStateBadge


def _map_module_name_to_section(name: str) -> AppSection | None:
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
    """Overview tab for employee safety state. / Вкладка обзора состояния допусков работника."""

    module_clicked = Signal(AppSection)

    def __init__(self, row: EmployeeWorkspaceRow) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["lg"], SPACING["lg"], SPACING["lg"], SPACING["lg"])
        layout.setSpacing(SPACING["lg"])

        headline = QFrame()
        headline.setObjectName("employeeOverviewHeadline")
        headline.setStyleSheet(
            f"""
            QFrame#employeeOverviewHeadline {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #FFFFFF, stop:1 #F5F8FC);
                border: 1px solid {COLOR['border_soft']};
                border-radius: {RADIUS['xl']}px;
            }}
            QLabel#employeeOverviewAnswer {{
                color: {COLOR['text_primary']};
                font-size: 16px;
                font-weight: 900;
                line-height: 1.35;
            }}
            """
        )
        headline_layout = QVBoxLayout(headline)
        headline_layout.setContentsMargins(SPACING["lg"], SPACING["lg"], SPACING["lg"], SPACING["lg"])
        answer = QLabel(_build_admission_headline(row))
        answer.setObjectName("employeeOverviewAnswer")
        answer.setWordWrap(True)
        headline_layout.addWidget(answer)
        layout.addWidget(headline)

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
        super().__init__()
        self.setObjectName("employeeModuleSummaryCard")
        self._target_section = _map_module_name_to_section(summary.module_name)
        if self._target_section:
            self.setCursor(Qt.CursorShape.PointingHandCursor)

        self.setStyleSheet(
            f"""
            QFrame#employeeModuleSummaryCard {{
                background: #FFFFFF;
                border: 1px solid {COLOR['border_soft']};
                border-radius: {RADIUS['xl']}px;
            }}
            QFrame#employeeModuleSummaryCard:hover {{
                border: 1px solid {COLOR['accent']};
                background: #F8FBFD;
            }}
            QLabel#employeeModuleTitle {{
                color: {COLOR['text_primary']};
                font-size: 15px;
                font-weight: 900;
            }}
            """
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["md"], SPACING["md"], SPACING["md"], SPACING["md"])
        layout.setSpacing(SPACING["sm"])

        title = QLabel(summary.module_name)
        title.setObjectName("employeeModuleTitle")
        layout.addWidget(title)
        layout.addWidget(EmployeeRowStateBadge(summary.level, summary.label))

        reason = QLabel(summary.reason)
        reason.setWordWrap(True)
        reason.setStyleSheet(f"color: {COLOR['text_secondary']}; font-size: 14px; font-weight: 600;")
        layout.addWidget(reason)

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton and self._target_section:
            self.clicked.emit(self._target_section)
        super().mousePressEvent(event)


def _build_admission_headline(row: EmployeeWorkspaceRow) -> str:
    if row.status_level == EmployeeStatusLevel.NORMAL:
        return "Зауважень не виявлено\nДопуск: до робіт допущений."
    return f"Увага! Немає допуску до робіт\nПричина: {row.status_reason}."
