"""
SectionContainer — контейнер-обгортка для екранів контенту.
Додає вертикальний скрол і однакові відступи для всіх розділів.
SectionContainer — scrollable wrapper container for content screens.
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QScrollArea, QVBoxLayout, QWidget

from osah.ui.qt.design.tokens import COLOR


class SectionContainer(QScrollArea):
    """Прокручуваний контейнер для контентних екранів.
    Scrollable content container for section screens.
    """

    def __init__(self) -> None:
        super().__init__()
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setFrameShape(QScrollArea.Shape.NoFrame)

        self._inner = QWidget()
        self._inner.setProperty("role", "section_bg")
        self._layout = QVBoxLayout(self._inner)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        self._layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.setWidget(self._inner)

    def content_layout(self) -> QVBoxLayout:
        """Повертає layout для розміщення вмісту екрану.
        Returns the layout for placing screen content.
        """
        return self._layout
