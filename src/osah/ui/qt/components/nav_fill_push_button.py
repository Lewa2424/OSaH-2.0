"""
NavFillPushButton - nav button with a smoothed diagnostic background.
NavFillPushButton - nav-кнопка со сглаженным диагностическим фоном.
"""

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QPushButton, QStyle, QStyleOptionButton

from osah.ui.qt.design.tokens import COLOR, FONT, RADIUS
from osah.ui.qt.design.ui_scale import scaled_px


class NavFillPushButton(QPushButton):
    """Navigation button with full-surface weighted gradient. / Навигационная кнопка с полноразмерным сглаженным градиентом."""

    def __init__(self, text: str) -> None:
        super().__init__(text)
        self._fill_colors: tuple[str, ...] | None = None
        self._problem_border = False
        self.setMouseTracking(True)

    def set_fill_colors(self, colors: tuple[str, ...] | None) -> None:
        """Updates the diagnostic palette. / Обновляет диагностическую палитру."""
        self._fill_colors = colors
        self.update()

    def set_problem_border(self, enabled: bool) -> None:
        """Toggles critical border state. / Переключает критическую рамку."""
        if self._problem_border != enabled:
            self._problem_border = enabled
            self.update()

    def enterEvent(self, event) -> None:  # noqa: N802
        super().enterEvent(event)
        self.update()

    def leaveEvent(self, event) -> None:  # noqa: N802
        super().leaveEvent(event)
        self.update()

    def paintEvent(self, _event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        option = QStyleOptionButton()
        self.initStyleOption(option)
        rect = QRectF(self.rect())
        radius = scaled_px(RADIUS["md"])

        path = QPainterPath()
        path.addRoundedRect(rect, radius, radius)

        painter.setClipPath(path)
        painter.fillPath(path, self._build_fill_brush(rect))

        if self.underMouse() and not self.isChecked():
            painter.fillRect(rect, QColor(255, 255, 255, 18))
        if option.state & QStyle.StateFlag.State_Sunken:
            painter.fillRect(rect, QColor(0, 0, 0, 26))

        painter.setClipping(False)

        border_color = self._resolve_border_color()
        border_width = 2 if self._problem_border and not self.isChecked() else 1
        painter.setPen(QPen(QColor(border_color), border_width))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        inset = border_width / 2
        painter.drawRoundedRect(rect.adjusted(inset, inset, -inset, -inset), radius, radius)

        painter.setPen(QColor(self._resolve_text_color()))
        label_font = QFont(FONT["nav_item"][0])
        label_font.setPixelSize(scaled_px(14))
        label_font.setBold(True)
        painter.setFont(label_font)
        text_rect = rect.adjusted(scaled_px(12), 0, -scaled_px(8), 0)
        painter.drawText(
            text_rect.toRect(),
            int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter),
            self.text(),
        )

    def _build_fill_brush(self, rect: QRectF):
        if self.isChecked():
            return QColor(COLOR["nav_item_active_bg"])
        if not self._fill_colors:
            return QColor(COLOR["bg_card"])

        gradient = QLinearGradient(rect.left(), rect.center().y(), rect.right(), rect.center().y())
        for stop, hex_color in _build_weighted_gradient_stops(self._fill_colors):
            gradient.setColorAt(stop, QColor(hex_color))
        return gradient

    def _resolve_border_color(self) -> str:
        if self.isChecked():
            return COLOR["nav_item_active_bg"]
        if self._problem_border:
            return COLOR["nav_item_problem_border"]
        return COLOR["border_default"]

    def _resolve_text_color(self) -> str:
        if self.isChecked():
            return COLOR["nav_item_active_text"]
        return COLOR["nav_item_text"]


def _build_weighted_gradient_stops(colors: tuple[str, ...]) -> tuple[tuple[float, str], ...]:
    """Builds smooth weighted gradient stops. / Строит плавные весовые остановки градиента."""

    if not colors:
        return ((0.0, COLOR["bg_card"]), (1.0, COLOR["bg_card"]))

    runs: list[tuple[str, int]] = []
    current_color = colors[0]
    current_count = 1
    for color in colors[1:]:
        if color == current_color:
            current_count += 1
            continue
        runs.append((current_color, current_count))
        current_color = color
        current_count = 1
    runs.append((current_color, current_count))

    total = float(sum(count for _, count in runs))
    accumulated = 0.0
    stops: list[tuple[float, str]] = [(0.0, runs[0][0])]

    for index, (color, count) in enumerate(runs):
        start_ratio = accumulated / total
        end_ratio = (accumulated + count) / total
        mid_ratio = (start_ratio + end_ratio) / 2.0
        stops.append((mid_ratio, color))

        if index < len(runs) - 1:
            next_color = runs[index + 1][0]
            edge_ratio = end_ratio
            spread = min(0.02, max(0.008, count / total / 3.0))
            left_ratio = max(0.0, edge_ratio - spread)
            right_ratio = min(1.0, edge_ratio + spread)
            blended = _mix_hex(color, next_color, 0.5)
            stops.append((left_ratio, color))
            stops.append((edge_ratio, blended))
            stops.append((right_ratio, next_color))
        accumulated += count

    stops.append((1.0, runs[-1][0]))
    return tuple(_dedupe_stops(sorted(stops, key=lambda item: item[0])))


def _dedupe_stops(stops: list[tuple[float, str]]) -> list[tuple[float, str]]:
    """Removes redundant stops. / Убирает избыточные остановки."""

    result: list[tuple[float, str]] = []
    for stop, color in stops:
        bounded_stop = max(0.0, min(1.0, stop))
        if result and abs(result[-1][0] - bounded_stop) < 0.0001 and result[-1][1] == color:
            continue
        result.append((bounded_stop, color))
    if result and result[0][0] != 0.0:
        result.insert(0, (0.0, result[0][1]))
    if result and result[-1][0] != 1.0:
        result.append((1.0, result[-1][1]))
    return result


def _mix_hex(start_hex: str, end_hex: str, ratio: float) -> str:
    """Mixes two colors. / Смешивает два цвета."""

    start = QColor(start_hex)
    end = QColor(end_hex)
    mix = max(0.0, min(1.0, ratio))
    inverse = 1.0 - mix
    return QColor(
        int(start.red() * inverse + end.red() * mix),
        int(start.green() * inverse + end.green() * mix),
        int(start.blue() * inverse + end.blue() * mix),
    ).name()
