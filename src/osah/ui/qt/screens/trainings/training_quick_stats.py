from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout

from osah.domain.entities.training_workspace_summary import TrainingWorkspaceSummary
from osah.ui.qt.design.tokens import COLOR, RADIUS, SPACING


class TrainingQuickStats(QFrame):
    """Швидкі показники модуля інструктажів.
    Quick metrics for the trainings module.
    """

    def __init__(self, summary: TrainingWorkspaceSummary) -> None:
        super().__init__()
        self.setObjectName("trainingQuickStats")
        self.setStyleSheet(
            f"QFrame#trainingQuickStats {{ "
            f"background: {COLOR['bg_card']}; border: 1px solid {COLOR['border_soft']};"
            f"border-radius: {RADIUS['xl']}px; "
            f"}}"
        )
        layout = QHBoxLayout(self)
        layout.setContentsMargins(SPACING["lg"], SPACING["md"], SPACING["lg"], SPACING["md"])
        layout.setSpacing(SPACING["lg"])
        self._total = _metric("Усього", summary.total_rows, COLOR["accent"])
        self._critical = _metric("Критично", summary.critical_total + summary.missing_total, COLOR["critical"])
        self._warning = _metric("Увага", summary.warning_total, COLOR["warning"])
        self._current = _metric("Актуально", summary.current_total, COLOR["success"])
        layout.addWidget(self._total)
        layout.addWidget(self._critical)
        layout.addWidget(self._warning)
        layout.addWidget(self._current)
        layout.addStretch()

    # ###### ОНОВЛЕННЯ МЕТРИК / UPDATE METRICS ######
    def set_summary(self, summary: TrainingWorkspaceSummary) -> None:
        """Оновлює числа quick stats після зміни даних.
        Updates quick-stats values after data changes.
        """

        _set_metric_value(self._total, summary.total_rows)
        _set_metric_value(self._critical, summary.critical_total + summary.missing_total)
        _set_metric_value(self._warning, summary.warning_total)
        _set_metric_value(self._current, summary.current_total)


def _metric(title: str, value: int, color: str) -> QFrame:
    """Створює одну компактну метрику quick stats.
    Creates one compact quick-stats metric.
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
