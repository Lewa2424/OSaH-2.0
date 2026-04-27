"""
Dashboard metric card component.
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from osah.ui.qt.components.animated_metric_border_frame import AnimatedMetricBorderFrame
from osah.ui.qt.design.tokens import COLOR, FONT, SPACING


class MetricCard(QWidget):
    """Compact KPI card for the dashboard top row."""

    def __init__(
        self,
        title: str,
        value: str,
        subtitle: str,
        accent_color: str,
    ) -> None:
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        self._card = AnimatedMetricBorderFrame(accent_color)
        self._card.setObjectName("metricCard")
        self._card.setMinimumHeight(88)

        outer_layout.addWidget(self._card)

        content_layout = QVBoxLayout(self._card)
        content_layout.setContentsMargins(
            SPACING["md"],
            SPACING["md"],
            SPACING["md"],
            SPACING["md"],
        )
        content_layout.setSpacing(3)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(
            f"color: {COLOR['metric_card_label']};"
            "font-size: 11px;"
            "font-weight: 700;"
        )
        content_layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)

        value_label = QLabel(value)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_font = QFont(FONT["metric"][0], FONT["metric"][1] + 2)
        value_font.setBold(FONT["metric"][2])
        value_label.setFont(value_font)
        value_label.setStyleSheet(f"color: {accent_color};")
        content_layout.addWidget(value_label, alignment=Qt.AlignmentFlag.AlignCenter)

        subtitle_label = QLabel(subtitle)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setWordWrap(True)
        subtitle_label.setStyleSheet(
            f"color: {COLOR['text_secondary']};"
            "font-size: 10px;"
            "font-weight: 400;"
        )
        content_layout.addWidget(subtitle_label, alignment=Qt.AlignmentFlag.AlignCenter)
