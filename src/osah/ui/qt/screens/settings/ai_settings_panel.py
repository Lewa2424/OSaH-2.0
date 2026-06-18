from PySide6.QtCore import Signal
from PySide6.QtWidgets import QCheckBox, QVBoxLayout, QWidget

from osah.ui.qt.components.section_header import SectionHeader
from osah.ui.qt.design.tokens import SPACING


class AiSettingsPanel(QWidget):
    """Панель налаштувань локального AI для інспектора.
    Inspector-only local AI settings panel.
    """

    prefer_fallback_model_changed = Signal(bool)

    def __init__(self, *, prefer_fallback_model: bool, read_only: bool) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING["sm"])
        layout.addWidget(
            SectionHeader(
                "ClearWork AI",
                "Локальний AI-помічник працює офлайн і доступний лише інспектору.",
            )
        )

        self._prefer_fallback_checkbox = QCheckBox("Використовувати легшу модель 1.5B для слабших ПК")
        self._prefer_fallback_checkbox.setChecked(prefer_fallback_model)
        self._prefer_fallback_checkbox.setEnabled(not read_only)
        self._prefer_fallback_checkbox.toggled.connect(self.prefer_fallback_model_changed.emit)
        layout.addWidget(self._prefer_fallback_checkbox)
