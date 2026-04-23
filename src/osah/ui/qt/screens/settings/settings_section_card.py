from PySide6.QtWidgets import QFrame, QVBoxLayout

from osah.ui.qt.design.tokens import SPACING


class SettingsSectionCard(QFrame):
    """Reusable section card for Settings screen blocks."""

    def __init__(self) -> None:
        super().__init__()
        self.setProperty("card", "true")
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(SPACING["lg"], SPACING["lg"], SPACING["lg"], SPACING["lg"])
        self._layout.setSpacing(SPACING["sm"])

    # ###### ДОСТУП ДО РОЗКЛАДКИ КАРТКИ / GET CARD LAYOUT ######
    def content_layout(self) -> QVBoxLayout:
        """Returns content layout for adding section widgets."""

        return self._layout
