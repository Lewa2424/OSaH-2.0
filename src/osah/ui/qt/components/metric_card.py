"""
MetricCard — картка метрики для Dashboard.
Відображає числовий показник з акцентною кольоровою смугою зліва.
MetricCard — Dashboard metric card with a colored left accent bar.
"""
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QFrame, QGraphicsDropShadowEffect, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from osah.ui.qt.design.tokens import COLOR, FONT, RADIUS, SPACING


class MetricCard(QWidget):
    """Картка з числовою метрикою та кольоровим акцентом.
    Metric card with color accent and shadow for dashboard display.
    """

    def __init__(
        self,
        title: str,
        value: str,
        subtitle: str,
        accent_color: str,
    ) -> None:
        super().__init__()

        # Зовнішня обгортка з тінню / Outer wrapper with shadow
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        # Фрейм-картка / Card frame
        card = QFrame()
        card.setProperty("card", "true")
        card.setMinimumHeight(110)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(16)
        shadow.setOffset(0, 2)
        shadow.setColor(__import__("PySide6.QtGui", fromlist=["QColor"]).QColor(0, 0, 0, 18))
        card.setGraphicsEffect(shadow)

        outer_layout.addWidget(card)

        # Горизонтальний layout: [акцент-бар | контент]
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        # Кольорова вертикальна смуга зліва / Left accent bar
        bar = QFrame()
        bar.setFixedWidth(4)
        bar.setStyleSheet(
            f"background: {accent_color};"
            f"border-top-left-radius: {RADIUS['xl']}px;"
            f"border-bottom-left-radius: {RADIUS['xl']}px;"
            f"border-top-right-radius: 0px;"
            f"border-bottom-right-radius: 0px;"
        )
        card_layout.addWidget(bar)

        # Контентна зона / Content zone
        content = QWidget()
        content.setStyleSheet("background: transparent;")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(
            SPACING["lg"], SPACING["lg"],
            SPACING["lg"], SPACING["lg"],
        )
        content_layout.setSpacing(4)
        card_layout.addWidget(content)

        # Назва / Title
        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: {COLOR['text_muted']}; font-size: 10px; font-weight: bold;")
        content_layout.addWidget(title_label)

        # Значення / Value
        value_label = QLabel(value)
        value_font = QFont(FONT["metric"][0], FONT["metric"][1])
        value_font.setBold(FONT["metric"][2])
        value_label.setFont(value_font)
        value_label.setStyleSheet(f"color: {COLOR['text_primary']};")
        content_layout.addWidget(value_label)

        # Підпис / Subtitle
        sub_label = QLabel(subtitle)
        sub_label.setWordWrap(True)
        sub_label.setStyleSheet(f"color: {COLOR['accent']}; font-size: 9px;")
        content_layout.addWidget(sub_label)

        content_layout.addStretch()
