from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from osah.ui.qt.design.tokens import COLOR, SPACING
from osah.version import __version__


class SectionInstructionDialog(QDialog):
    """Модальний екран детальної інструкції по розділу ClearWork.
    Modal full instruction screen for a ClearWork app section.
    """

    def __init__(
        self,
        title: str,
        subtitle: str,
        content: QWidget,
        *,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"Інструкція — {title}")
        self.setModal(True)

        screen = self.screen()
        max_height = 820
        if screen is not None:
            max_height = max(640, screen.availableGeometry().height() - 80)
        self.resize(920, min(820, max_height))
        self.setStyleSheet(f"QDialog {{ background: {COLOR['bg_card']}; }}")

        root = QVBoxLayout(self)
        root.setContentsMargins(SPACING["lg"], SPACING["lg"], SPACING["lg"], SPACING["lg"])
        root.setSpacing(SPACING["md"])

        header = QLabel(title)
        header_font = QFont("Segoe UI", 20)
        header_font.setBold(True)
        header.setFont(header_font)
        root.addWidget(header)

        if subtitle.strip():
            sub = QLabel(subtitle)
            sub.setWordWrap(True)
            sub.setStyleSheet(f"color: {COLOR['text_secondary']}; font-size: 13px;")
            root.addWidget(sub)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setWidget(content)
        root.addWidget(scroll, stretch=1)

        footer = QLabel(f"Матеріали за станом ClearWork {__version__}")
        footer.setStyleSheet(f"color: {COLOR['text_muted']}; font-size: 11px;")
        root.addWidget(footer)

        buttons = QHBoxLayout()
        buttons.addStretch()
        close_btn = QPushButton("Закрити")
        close_btn.setProperty("variant", "secondary")
        close_btn.clicked.connect(self.accept)
        buttons.addWidget(close_btn)
        root.addLayout(buttons)
