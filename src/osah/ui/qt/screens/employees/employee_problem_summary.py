from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout

from osah.domain.entities.employee_problem import EmployeeProblem
from osah.domain.entities.employee_status_level import EmployeeStatusLevel
from osah.ui.qt.design.tokens import COLOR, RADIUS, SPACING


class EmployeeProblemSummary(QFrame):
    """Problem reason block in the employee card."""

    def __init__(self, problems: tuple[EmployeeProblem, ...]) -> None:
        super().__init__()
        self.setObjectName("employeeProblemSummary")
        self.setStyleSheet(
            f"QFrame#employeeProblemSummary {{ "
            f"background: {COLOR['bg_panel']}; border: 1px solid {COLOR['border_soft']}; "
            f"border-radius: {RADIUS['lg']}px; "
            f"}}"
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["lg"], SPACING["md"], SPACING["lg"], SPACING["md"])
        layout.setSpacing(SPACING["sm"])

        title = QLabel("Причини та сигнали")
        title.setStyleSheet("font-weight: 800; font-size: 13px;")
        layout.addWidget(title)

        if not problems:
            empty = QLabel("Блокуючих причин або попереджень немає.")
            empty.setStyleSheet(f"color: {COLOR['success']};")
            layout.addWidget(empty)
            return

        for problem in problems[:6]:
            label = QLabel(_format_problem_line(problem))
            label.setWordWrap(True)
            label.setStyleSheet(f"color: {_color_for_problem(problem.level)}; font-weight: 600;")
            layout.addWidget(label)


def _format_problem_line(problem: EmployeeProblem) -> str:
    """###### РЯДОК ПРОБЛЕМИ / PROBLEM LINE ######"""

    return f"{_marker_for_problem(problem.level)} {problem.module_name}: {problem.title}"


def _marker_for_problem(level: EmployeeStatusLevel) -> str:
    """###### МАРКЕР РІВНЯ / LEVEL MARKER ######"""

    if level == EmployeeStatusLevel.CRITICAL:
        return "!"
    if level == EmployeeStatusLevel.WARNING:
        return "i"
    if level == EmployeeStatusLevel.RESTRICTED:
        return "~"
    return "-"


def _color_for_problem(level: EmployeeStatusLevel) -> str:
    """###### КОЛІР ПРОБЛЕМИ / PROBLEM COLOR ######"""

    if level == EmployeeStatusLevel.CRITICAL:
        return COLOR["critical"]
    if level == EmployeeStatusLevel.WARNING:
        return COLOR["warning"]
    if level == EmployeeStatusLevel.RESTRICTED:
        return COLOR["restricted"]
    return COLOR["text_secondary"]
