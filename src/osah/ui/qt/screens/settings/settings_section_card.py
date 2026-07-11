from PySide6.QtGui import QColor
from PySide6.QtWidgets import QFrame, QGraphicsDropShadowEffect, QVBoxLayout

from osah.ui.qt.design.tokens import SPACING


class SettingsSectionCard(QFrame):
    """Reusable section card for Settings screen blocks."""

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("settingsSectionCard")
        self.setStyleSheet(
            """
            QFrame#settingsSectionCard {
                background:
                    qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 rgba(255, 255, 255, 246),
                        stop:0.55 rgba(244, 248, 252, 238),
                        stop:1 rgba(233, 241, 249, 228));
                border: 1px solid rgba(132, 164, 197, 0.55);
                border-radius: 26px;
            }
            """
        )
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(26)
        shadow.setOffset(0, 10)
        shadow.setColor(QColor(27, 57, 96, 28))
        self.setGraphicsEffect(shadow)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(SPACING["lg"], SPACING["lg"], SPACING["lg"], SPACING["lg"])
        self._layout.setSpacing(SPACING["sm"])

    # ###### ДОСТУП ДО РОЗКЛАДКИ КАРТКИ / GET CARD LAYOUT ######
    def content_layout(self) -> QVBoxLayout:
        """Returns content layout for adding section widgets."""

        return self._layout
