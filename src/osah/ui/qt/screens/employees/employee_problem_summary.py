from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout

from osah.domain.entities.employee_problem import EmployeeProblem
from osah.domain.entities.employee_status_level import EmployeeStatusLevel
from osah.ui.qt.design.tokens import COLOR, RADIUS, SPACING


class EmployeeProblemSummary(QFrame):
    """Problem reason block in the employee card. / Блок сигналов и причин в карточке работника."""

    def __init__(self, problems: tuple[EmployeeProblem, ...]) -> None:
        super().__init__()
        self.setObjectName("employeeProblemSummary")
        self.setStyleSheet(
            f"""
            QFrame#employeeProblemSummary {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #F2F6FB, stop:1 #E8EEF6);
                border: 1px solid {COLOR['border_soft']};
                border-radius: {RADIUS['xl']}px;
            }}
            QLabel#employeeProblemTitle {{
                color: {COLOR['text_primary']};
                font-size: 15px;
                font-weight: 900;
            }}
            """
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["lg"], SPACING["md"], SPACING["lg"], SPACING["md"])
        layout.setSpacing(SPACING["sm"])

        title = QLabel("Сигнали та причини")
        title.setObjectName("employeeProblemTitle")
        layout.addWidget(title)

        if not problems:
            empty = QLabel("Блокуючих причин або попереджень немає.")
            empty.setStyleSheet(f"color: {COLOR['success']}; font-size: 14px; font-weight: 700;")
            layout.addWidget(empty)
            return

        for problem in problems[:6]:
            label = QLabel(_format_problem_line(problem))
            label.setWordWrap(True)
            label.setStyleSheet(
                f"color: {_color_for_problem(problem.level)}; font-size: 14px; font-weight: 700; line-height: 1.35;"
            )
            layout.addWidget(label)


def _format_problem_line(problem: EmployeeProblem) -> str:
    return f"{_marker_for_problem(problem.level)} {problem.module_name}: {problem.title}"


def _marker_for_problem(level: EmployeeStatusLevel) -> str:
    if level == EmployeeStatusLevel.CRITICAL:
        return "!"
    if level == EmployeeStatusLevel.WARNING:
        return "i"
    if level == EmployeeStatusLevel.RESTRICTED:
        return "~"
    return "-"


def _color_for_problem(level: EmployeeStatusLevel) -> str:
    if level == EmployeeStatusLevel.CRITICAL:
        return COLOR["critical"]
    if level == EmployeeStatusLevel.WARNING:
        return COLOR["warning"]
    if level == EmployeeStatusLevel.RESTRICTED:
        return COLOR["restricted"]
    return COLOR["text_secondary"]
