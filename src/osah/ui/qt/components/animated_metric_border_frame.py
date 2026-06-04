"""
Animated border frame for dashboard KPI cards.
"""

from PySide6.QtCore import Property, QEasingCurve, QRectF, Qt, QPropertyAnimation, QVariantAnimation
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QFrame

from osah.ui.qt.design.tokens import ANIMATION, COLOR, RADIUS


class AnimatedMetricBorderFrame(QFrame):
    """Frame that draws a smooth hover background transition and a one-shot rotating border highlight."""

    def __init__(self, accent_color: str) -> None:
        super().__init__()
        self._accent_color = QColor(accent_color)
        self._normal_bg = QColor(COLOR["metric_card_bg"])
        self._hover_bg = QColor(COLOR["card_hover_bg"])
        self._scan_progress = 0.0
        self._hover_progress = 0.0
        self._scan_animation: QPropertyAnimation | None = None
        self._hover_animation: QVariantAnimation | None = None
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)

    def get_scan_progress(self) -> float:
        """Повертає прогрес обертання контуру. Returns rotating border progress."""
        return self._scan_progress

    def set_scan_progress(self, value: float) -> None:
        """Оновлює прогрес і перемальовує контур. Updates scan progress and repaints."""
        self._scan_progress = max(0.0, min(1.0, value))
        self.update()

    scanProgress = Property(float, get_scan_progress, set_scan_progress)

    def enterEvent(self, event) -> None:  # noqa: N802
        """Плавно вмикає hover-стан і запускає сканування. Smoothly activates hover and starts scan."""
        self._start_hover_transition(1.0)
        self._start_scan_animation()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:  # noqa: N802
        """Плавно вимикає hover-стан. Smoothly deactivates hover state."""
        self._start_hover_transition(0.0)
        if self._scan_animation:
            self._scan_animation.stop()
        self.set_scan_progress(0.0)
        super().leaveEvent(event)

    def paintEvent(self, event) -> None:  # noqa: N802
        """Малює фон (з плавним переходом hover), базову рамку і scan-сегменти."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        rect = QRectF(self.rect()).adjusted(1.5, 1.5, -1.5, -1.5)
        radius = float(RADIUS["xl"])

        background = _mix_colors(self._normal_bg, self._hover_bg, self._hover_progress)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(background)
        painter.drawRoundedRect(rect, radius, radius)

        base_pen = QPen(self._accent_color, 2)
        base_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(base_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(rect, radius, radius)

        if self._scan_progress > 0.0:
            self._paint_scan_segments(painter, rect, radius)

        super().paintEvent(event)

    def _start_hover_transition(self, target: float) -> None:
        """Запускає плавний перехід hover_progress до target. Starts smooth hover_progress transition."""
        if self._hover_animation is not None:
            self._hover_animation.stop()

        start = self._hover_progress
        animation = QVariantAnimation(self)
        animation.setDuration(ANIMATION["fast"])
        animation.setStartValue(start)
        animation.setEndValue(target)
        animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        animation.valueChanged.connect(self._on_hover_progress_changed)
        animation.start()
        self._hover_animation = animation

    def _on_hover_progress_changed(self, value: object) -> None:
        """Зберігає поточний прогрес hover і тригерить перемальовування."""
        self._hover_progress = float(value)
        self.update()

    def _start_scan_animation(self) -> None:
        """Створює анімацію проходу по контуру. Creates one-shot border scan animation."""
        if self._scan_animation:
            self._scan_animation.stop()

        self.set_scan_progress(0.001)
        self._scan_animation = QPropertyAnimation(self, b"scanProgress", self)
        self._scan_animation.setDuration(ANIMATION["normal"] * 3)
        self._scan_animation.setStartValue(0.001)
        self._scan_animation.setEndValue(1.0)
        self._scan_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self._scan_animation.finished.connect(self._finish_scan_animation)
        self._scan_animation.start()

    def _finish_scan_animation(self) -> None:
        """Завершує scan і лишає звичайну рамку. Ends scan and leaves normal border."""
        self.set_scan_progress(0.0)

    def _paint_scan_segments(self, painter: QPainter, rect: QRectF, radius: float) -> None:
        """Малює чотири рухомі світлові сегменти. Paints four moving highlight segments."""
        path = QPainterPath()
        path.addRoundedRect(rect, radius, radius)
        segment_length = 0.07
        samples = 11

        for quarter in (0.0, 0.25, 0.5, 0.75):
            start = (self._scan_progress + quarter) % 1.0
            self._paint_path_segment(painter, path, start, segment_length, samples)

    def _paint_path_segment(
        self,
        painter: QPainter,
        path: QPainterPath,
        start: float,
        length: float,
        samples: int,
    ) -> None:
        """Малює один сегмент з яскравою головою і градієнтним хвостом."""
        bright = self._accent_color.lighter(250)
        dim = self._accent_color.darker(200)

        for index in range(samples):
            segment_start = (start + length * index / samples) % 1.0
            segment_end = (start + length * (index + 1) / samples) % 1.0
            if segment_end < segment_start:
                continue

            color_ratio = index / max(1, samples - 1)
            color = _mix_colors(bright, dim, color_ratio)
            pen = QPen(color, 3)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.drawLine(path.pointAtPercent(segment_start), path.pointAtPercent(segment_end))


def _mix_colors(start: QColor, end: QColor, progress: float) -> QColor:
    """Змішує два QColor за прогресом [0..1]. Mixes two QColors by progress [0..1]."""
    progress = max(0.0, min(1.0, progress))
    red = int(start.red() + (end.red() - start.red()) * progress)
    green = int(start.green() + (end.green() - start.green()) * progress)
    blue = int(start.blue() + (end.blue() - start.blue()) * progress)
    return QColor(red, green, blue)
