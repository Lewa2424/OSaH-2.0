"""
Dashboard metric card component.
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QFontMetrics
from PySide6.QtWidgets import QLabel, QSizePolicy, QVBoxLayout, QWidget

from osah.ui.qt.components.animated_metric_border_frame import AnimatedMetricBorderFrame
from osah.ui.qt.design.tokens import COLOR, FONT, SPACING

_METRIC_FONT_SCALE = 5 / 3  # +2/3 від базового розміру для назви та пояснення
_TITLE_FONT_PX = round(14 * _METRIC_FONT_SCALE)
_VALUE_FONT_PX = 30
_VALUE_LINE_HEIGHT_PX = 33
_SUBTITLE_FONT_PX = round(12 * _METRIC_FONT_SCALE)
_LINE_GAP_PX = 4


def _build_pixel_font(size_px: int, *, bold: bool) -> QFont:
    """Повертає шрифт у пікселях (для метрик розміру). Returns a pixel-sized QFont for metrics."""

    font = QFont(FONT["metric"][0])
    font.setPixelSize(size_px)
    font.setBold(bold)
    return font


def _ink_line_height(font: QFont, sample_text: str) -> int:
    """Реальна висота «чорнил» рядка без зайвого боксу шрифту.
    Actual ink height of a line without the extra font box.
    """

    metrics = QFontMetrics(font)
    probe_text = sample_text.strip() or "Ag"
    tight_height = metrics.tightBoundingRect(probe_text).height()
    cap_height = metrics.capHeight()
    return max(tight_height, cap_height) + metrics.descent() + 4


def _configure_single_line_label(
    label: QLabel,
    size_px: int,
    *,
    bold: bool,
    color: str,
    sample_text: str,
    line_height_px: int | None = None,
) -> int:
    """Налаштовує QLabel в одну щільну лінію. Configures a tight single-line QLabel."""

    font = _build_pixel_font(size_px, bold=bold)
    label.setFont(font)
    line_height = line_height_px if line_height_px is not None else _ink_line_height(font, sample_text)
    label.setFixedHeight(line_height)
    label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
    label.setWordWrap(False)
    label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    label.setStyleSheet(
        f"color: {color};"
        f"font-size: {size_px}px;"
        f"font-weight: {'700' if bold else '400'};"
        "background: transparent;"
    )
    return line_height


class MetricCard(QWidget):
    """Compact KPI card for the dashboard top row."""

    def __init__(
        self,
        title: str,
        value: str,
        subtitle: str,
        accent_color: str,
        *,
        size_scale: float = 1.0,
    ) -> None:
        super().__init__()
        scale = max(0.5, min(size_scale, 1.5))
        title_font_px = round(_TITLE_FONT_PX * scale)
        value_font_px = round(_VALUE_FONT_PX * scale)
        value_line_height_px = round(_VALUE_LINE_HEIGHT_PX * scale)
        subtitle_font_px = round(_SUBTITLE_FONT_PX * scale)
        line_gap_px = max(2, round(_LINE_GAP_PX * scale))
        horizontal_margin = max(4, round(SPACING["md"] * scale))
        vertical_margin = max(2, round(SPACING["xs"] * scale))

        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
        self._title_text = title
        self._subtitle_text = subtitle

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        self._card = AnimatedMetricBorderFrame(accent_color)
        self._card.setObjectName("metricCard")
        self._card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        outer_layout.addWidget(self._card)

        vertical_padding = vertical_margin * 2
        content_layout = QVBoxLayout(self._card)
        content_layout.setContentsMargins(
            horizontal_margin,
            vertical_margin,
            horizontal_margin,
            vertical_margin,
        )
        content_layout.setSpacing(line_gap_px)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

        self._title_label = QLabel(title)
        title_line_height = _configure_single_line_label(
            self._title_label,
            title_font_px,
            bold=True,
            color=COLOR["metric_card_label"],
            sample_text=title,
        )
        content_layout.addWidget(self._title_label)

        value_label = QLabel(value)
        value_line_height = _configure_single_line_label(
            value_label,
            value_font_px,
            bold=True,
            color=accent_color,
            sample_text=value,
            line_height_px=value_line_height_px,
        )
        content_layout.addWidget(value_label)

        self._subtitle_label = QLabel(subtitle)
        subtitle_line_height = _configure_single_line_label(
            self._subtitle_label,
            subtitle_font_px,
            bold=False,
            color=COLOR["text_secondary"],
            sample_text=subtitle,
        )
        content_layout.addWidget(self._subtitle_label)

        content_height = (
            title_line_height
            + line_gap_px
            + value_line_height
            + line_gap_px
            + subtitle_line_height
        )
        self._card.setFixedHeight(vertical_padding + content_height)

    def resizeEvent(self, event) -> None:  # noqa: N802
        """###### ОНОВЛЕННЯ ПІДІЗ ТЕКСТУ / UPDATE ELIDED LABELS ######"""

        super().resizeEvent(event)
        self._apply_single_line_texts()

    def showEvent(self, event) -> None:  # noqa: N802
        """###### ПЕРШИЙ ПОКАЗ КАРТКИ / FIRST SHOW ######"""

        super().showEvent(event)
        self._apply_single_line_texts()

    def _apply_single_line_texts(self) -> None:
        """Стискає довгі рядки в одну лінію з ellipsis.
        Fits long title/subtitle into a single line with ellipsis.
        """

        title_width = max(self._title_label.width(), 1)
        subtitle_width = max(self._subtitle_label.width(), 1)
        title_metrics = QFontMetrics(self._title_label.font())
        subtitle_metrics = QFontMetrics(self._subtitle_label.font())
        self._title_label.setText(
            title_metrics.elidedText(self._title_text, Qt.TextElideMode.ElideRight, title_width)
        )
        self._subtitle_label.setText(
            subtitle_metrics.elidedText(self._subtitle_text, Qt.TextElideMode.ElideRight, subtitle_width)
        )
