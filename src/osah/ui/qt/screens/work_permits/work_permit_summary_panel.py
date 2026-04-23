from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout

from osah.domain.entities.work_permit_workspace_summary import WorkPermitWorkspaceSummary
from osah.ui.qt.design.tokens import COLOR, RADIUS, SPACING


class WorkPermitSummaryPanel(QFrame):
    """Швидкі показники модуля нарядів-допусків.
    Quick metrics for the work permits module.
    """

    def __init__(self, summary: WorkPermitWorkspaceSummary) -> None:
        super().__init__()
        self.setStyleSheet(
            f"background: {COLOR['bg_card']}; border: 1px solid {COLOR['border_soft']};"
            f"border-radius: {RADIUS['xl']}px;"
        )
        layout = QHBoxLayout(self)
        layout.setContentsMargins(SPACING["lg"], SPACING["md"], SPACING["lg"], SPACING["md"])
        layout.setSpacing(SPACING["lg"])
        self._active = _metric("Діють", summary.active_total, COLOR["success"])
        self._warning = _metric("Скоро спливають", summary.warning_total, COLOR["warning"])
        self._expired = _metric("Критично", summary.expired_total, COLOR["critical"])
        self._conflicts = _metric("Конфлікти", summary.conflict_total, COLOR["critical"])
        self._participants = _metric("Учасники активних робіт", summary.active_participants_total, COLOR["accent"])
        for widget in (self._active, self._warning, self._expired, self._conflicts, self._participants):
            layout.addWidget(widget)
        layout.addStretch()

    # ###### ОНОВЛЕННЯ ПІДСУМКУ / UPDATE SUMMARY ######
    def set_summary(self, summary: WorkPermitWorkspaceSummary) -> None:
        """Оновлює числа quick stats після зміни даних.
        Updates quick-stats values after data changes.
        """

        _set_metric_value(self._active, summary.active_total)
        _set_metric_value(self._warning, summary.warning_total)
        _set_metric_value(self._expired, summary.expired_total)
        _set_metric_value(self._conflicts, summary.conflict_total)
        _set_metric_value(self._participants, summary.active_participants_total)


# ###### МЕТРИКА / METRIC ######
def _metric(title: str, value: int, color: str) -> QFrame:
    """Створює одну компактну метрику нарядів.
    Creates one compact work permit metric.
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


# ###### ОНОВЛЕННЯ МЕТРИКИ / UPDATE METRIC ######
def _set_metric_value(frame: QFrame, value: int) -> None:
    """Оновлює числове значення в метриці.
    Updates a numeric value in a metric.
    """

    label = frame.layout().itemAt(1).widget()
    if isinstance(label, QLabel):
        label.setText(str(value))
