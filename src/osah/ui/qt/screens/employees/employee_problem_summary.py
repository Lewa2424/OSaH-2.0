from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout

from osah.domain.entities.employee_problem import EmployeeProblem
from osah.domain.entities.employee_status_level import EmployeeStatusLevel
from osah.ui.qt.design.tokens import COLOR, RADIUS, SPACING


class EmployeeProblemSummary(QFrame):
    """Блок причин проблем у картці працівника.
    Problem reason block in the employee card.
    """

    def __init__(self, problems: tuple[EmployeeProblem, ...]) -> None:
        super().__init__()
        self.setStyleSheet(
            f"background: {COLOR['bg_panel']}; border: 1px solid {COLOR['border_soft']}; "
            f"border-radius: {RADIUS['lg']}px;"
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


# ###### РЯДОК ПРОБЛЕМИ / PROBLEM LINE ######
def _format_problem_line(problem: EmployeeProblem) -> str:
    """Форматує проблему як короткий зрозумілий рядок для користувача.
    Formats a problem as a short user-readable line.
    """

    return f"{_marker_for_problem(problem.level)} {problem.module_name}: {problem.title}"


def _marker_for_problem(level: EmployeeStatusLevel) -> str:
    """Повертає текстовий маркер рівня проблеми без залежності тільки від кольору.
    Returns a textual problem marker so status is not color-only.
    """

    if level == EmployeeStatusLevel.CRITICAL:
        return "!"
    if level == EmployeeStatusLevel.WARNING:
        return "i"
    if level == EmployeeStatusLevel.RESTRICTED:
        return "~"
    return "-"


def _color_for_problem(level: EmployeeStatusLevel) -> str:
    """Повертає колір проблеми для візуального акценту.
    Returns problem color for visual emphasis.
    """

    if level == EmployeeStatusLevel.CRITICAL:
        return COLOR["critical"]
    if level == EmployeeStatusLevel.WARNING:
        return COLOR["warning"]
    if level == EmployeeStatusLevel.RESTRICTED:
        return "#4338CA"
    return COLOR["text_secondary"]
