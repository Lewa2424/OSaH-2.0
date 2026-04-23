from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout

from osah.domain.entities.medical_workspace_summary import MedicalWorkspaceSummary
from osah.ui.qt.design.tokens import COLOR, RADIUS, SPACING


class MedicalSummaryPanel(QFrame):
    """Швидкі показники модуля медицини.
    Quick metrics for the medical module.
    """

    def __init__(self, summary: MedicalWorkspaceSummary) -> None:
        super().__init__()
        self.setStyleSheet(
            f"background: {COLOR['bg_card']}; border: 1px solid {COLOR['border_soft']};"
            f"border-radius: {RADIUS['xl']}px;"
        )
        layout = QHBoxLayout(self)
        layout.setContentsMargins(SPACING["lg"], SPACING["md"], SPACING["lg"], SPACING["md"])
        layout.setSpacing(SPACING["lg"])
        self._total = _metric("Усього", summary.total_rows, COLOR["accent"])
        self._critical = _metric("Не допущено", summary.critical_total, COLOR["critical"])
        self._restricted = _metric("Обмежено", summary.restricted_total, "#4338CA")
        self._warning = _metric("Увага", summary.warning_total, COLOR["warning"])
        self._current = _metric("Допущено", summary.current_total, COLOR["success"])
        for widget in (self._total, self._critical, self._restricted, self._warning, self._current):
            layout.addWidget(widget)
        layout.addStretch()

    def set_summary(self, summary: MedicalWorkspaceSummary) -> None:
        """Оновлює числа quick stats після зміни даних.
        Updates quick-stats values after data changes.
        """

        _set_metric_value(self._total, summary.total_rows)
        _set_metric_value(self._critical, summary.critical_total)
        _set_metric_value(self._restricted, summary.restricted_total)
        _set_metric_value(self._warning, summary.warning_total)
        _set_metric_value(self._current, summary.current_total)


def _metric(title: str, value: int, color: str) -> QFrame:
    """Створює одну компактну метрику медицини.
    Creates one compact medical metric.
    """

    frame = QFrame()
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(0, 0, 0, 0)
    label = QLabel(title)
    label.setStyleSheet(f"color: {COLOR['text_muted']}; font-weight: 700;")
    number = QLabel(str(value))
    number.setStyleSheet(f"color: {color}; font-size: 20px; font-weight: 900;")
    layout.addWidget(label)
    layout.addWidget(number)
    return frame


def _set_metric_value(frame: QFrame, value: int) -> None:
    """Оновлює числове значення в готовій метриці.
    Updates numeric value in an existing metric.
    """

    label = frame.layout().itemAt(1).widget()
    if isinstance(label, QLabel):
        label.setText(str(value))
