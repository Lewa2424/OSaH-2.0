from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QSizePolicy


class InfoTooltipIcon(QLabel):
    """Маленькая иконка с нормативной подсказкой рядом с подписью поля.
    Small info icon that shows a normative tooltip near a field label.
    """

    def __init__(self, tooltip_text: str) -> None:
        super().__init__("ⓘ")
        self.setToolTip(tooltip_text)
        self.setWordWrap(False)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCursor(Qt.CursorShape.WhatsThisCursor)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setStyleSheet("color: #5f6b7a; font-weight: 700; padding-left: 4px;")
