from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout

from osah.domain.entities.medical_workspace_summary import MedicalWorkspaceSummary
from osah.ui.qt.design.tokens import COLOR, RADIUS, SPACING


class MedicalSummaryPanel(QFrame):
    """Quick metrics for the medical module."""

    def __init__(self, summary: MedicalWorkspaceSummary) -> None:
        super().__init__()
        self.setObjectName("medicalSummaryPanel")
        self.setStyleSheet(
            f"QFrame#medicalSummaryPanel {{ "
            f"background: {COLOR['bg_card']}; border: 1px solid {COLOR['border_soft']};"
            f"border-radius: {RADIUS['xl']}px; "
            f"}}"
        )
        layout = QHBoxLayout(self)
        layout.setContentsMargins(SPACING["lg"], SPACING["md"], SPACING["lg"], SPACING["md"])
        layout.setSpacing(SPACING["lg"])
        self._total = _metric("Усього", summary.total_rows, COLOR["accent"])
        self._critical = _metric("Не допущено", summary.critical_total, COLOR["critical"])
        self._restricted = _metric("Обмежено", summary.restricted_total, COLOR["restricted"])
        self._warning = _metric("Увага", summary.warning_total, COLOR["warning"])
        self._current = _metric("Допущено", summary.current_total, COLOR["success"])
        for widget in (self._total, self._critical, self._restricted, self._warning, self._current):
            layout.addWidget(widget)
        layout.addStretch()

    def set_summary(self, summary: MedicalWorkspaceSummary) -> None:
        """###### ОНОВЛЕННЯ ПОКАЗНИКІВ / UPDATE METRICS ######"""

        _set_metric_value(self._total, summary.total_rows)
        _set_metric_value(self._critical, summary.critical_total)
        _set_metric_value(self._restricted, summary.restricted_total)
        _set_metric_value(self._warning, summary.warning_total)
        _set_metric_value(self._current, summary.current_total)


def _metric(title: str, value: int, color: str) -> QFrame:
    """###### ЕЛЕМЕНТ МЕТРИКИ / METRIC ITEM ######"""

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
    """###### ЗМІНА ЗНАЧЕННЯ / SET METRIC VALUE ######"""

    label = frame.layout().itemAt(1).widget()
    if isinstance(label, QLabel):
        label.setText(str(value))
