"""
Dashboard motion widgets for the redesigned main screen.
Локальные motion-виджеты дашборда для переработанного главного экрана.
"""

from PySide6.QtCore import QEasingCurve, QParallelAnimationGroup, QPropertyAnimation, QRectF, QSequentialAnimationGroup, QTimer, Qt, Property
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPen, QRadialGradient
from PySide6.QtWidgets import QFrame, QVBoxLayout, QWidget

from osah.ui.qt.design.tokens import COLOR, RADIUS, SPACING


class AmbientDashboardWidget(QWidget):
    """Animated ambient dashboard background. Анимированный фоновый слой дашборда."""

    def __init__(self) -> None:
        super().__init__()
        self._phase = 0.0
        self._timer = QTimer(self)
        self._timer.setInterval(33)
        self._timer.timeout.connect(self._advance_phase)
        self._timer.start()
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

    def _advance_phase(self) -> None:
        self._phase = (self._phase + 0.006) % 1.0
        self.update()

    def paintEvent(self, _event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        rect = QRectF(self.rect())
        painter.fillRect(rect, QColor(COLOR["bg_workspace"]))

        base_gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
        base_gradient.setColorAt(0.0, QColor("#EEF3F8"))
        base_gradient.setColorAt(0.40, QColor("#D7E0EA"))
        base_gradient.setColorAt(1.0, QColor("#F8FBFD"))
        painter.fillRect(rect, base_gradient)

        self._paint_orb(
            painter,
            rect,
            center_x=rect.width() * (0.18 + 0.06 * self._phase),
            center_y=rect.height() * 0.16,
            radius=max(rect.width(), rect.height()) * 0.26,
            inner=QColor(58, 95, 138, 72),
            outer=QColor(58, 95, 138, 0),
        )
        self._paint_orb(
            painter,
            rect,
            center_x=rect.width() * 0.78,
            center_y=rect.height() * (0.28 + 0.08 * (1.0 - self._phase)),
            radius=max(rect.width(), rect.height()) * 0.22,
            inner=QColor(6, 105, 196, 52),
            outer=QColor(6, 105, 196, 0),
        )
        self._paint_orb(
            painter,
            rect,
            center_x=rect.width() * 0.55,
            center_y=rect.height() * 0.84,
            radius=max(rect.width(), rect.height()) * 0.18,
            inner=QColor(252, 173, 15, 36),
            outer=QColor(252, 173, 15, 0),
        )

        self._paint_grid(painter, rect)
        self._paint_sweep(painter, rect)

    def _paint_orb(
        self,
        painter: QPainter,
        rect: QRectF,
        *,
        center_x: float,
        center_y: float,
        radius: float,
        inner: QColor,
        outer: QColor,
    ) -> None:
        gradient = QRadialGradient(center_x, center_y, radius)
        gradient.setColorAt(0.0, inner)
        gradient.setColorAt(1.0, outer)
        painter.fillRect(rect, gradient)

    def _paint_grid(self, painter: QPainter, rect: QRectF) -> None:
        minor_pen = QPen(QColor(17, 24, 39, 11), 1)
        major_pen = QPen(QColor(17, 24, 39, 18), 1)

        x_step = 36
        y_step = 28
        for x_pos in range(0, int(rect.width()), x_step):
            painter.setPen(major_pen if x_pos % (x_step * 4) == 0 else minor_pen)
            painter.drawLine(x_pos, 0, x_pos, int(rect.height()))
        for y_pos in range(0, int(rect.height()), y_step):
            painter.setPen(major_pen if y_pos % (y_step * 4) == 0 else minor_pen)
            painter.drawLine(0, y_pos, int(rect.width()), y_pos)

    def _paint_sweep(self, painter: QPainter, rect: QRectF) -> None:
        sweep_width = max(140.0, rect.width() * 0.18)
        x_pos = -sweep_width + (rect.width() + sweep_width * 2.0) * self._phase
        gradient = QLinearGradient(x_pos, 0, x_pos + sweep_width, 0)
        gradient.setColorAt(0.0, QColor(255, 255, 255, 0))
        gradient.setColorAt(0.45, QColor(255, 255, 255, 0))
        gradient.setColorAt(0.50, QColor(255, 255, 255, 44))
        gradient.setColorAt(0.55, QColor(255, 255, 255, 0))
        gradient.setColorAt(1.0, QColor(255, 255, 255, 0))
        painter.fillRect(rect, gradient)
        painter.end()


class SlideRevealFrame(QFrame):
    """Frame with pronounced slide-fade reveal. Контейнер с заметным reveal-эффектом."""

    def __init__(self) -> None:
        super().__init__()
        self._lift = 28.0
        self._started = False
        self._delay_ms = 0

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("background: transparent; border: none;")

        self._outer_layout = QVBoxLayout(self)
        self._outer_layout.setContentsMargins(0, round(self._lift), 0, 0)
        self._outer_layout.setSpacing(0)

        self._content = QFrame()
        self._content.setStyleSheet("background: transparent; border: none;")
        self._content_layout = QVBoxLayout(self._content)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(0)
        self._outer_layout.addWidget(self._content)

    def content_layout(self) -> QVBoxLayout:
        """Returns inner layout for actual content. Повертає внутренний layout для содержимого."""

        return self._content_layout

    def set_reveal_delay(self, delay_ms: int) -> None:
        """Sets reveal delay in milliseconds. Устанавливает задержку reveal в миллисекундах."""

        self._delay_ms = max(0, delay_ms)

    def get_lift(self) -> float:
        """Returns current reveal lift. Возвращает текущий вертикальный сдвиг reveal."""

        return self._lift

    def set_lift(self, value: float) -> None:
        """Updates reveal lift and margins. Обновляет вертикальный сдвиг и отступы."""

        self._lift = max(0.0, value)
        self._outer_layout.setContentsMargins(0, round(self._lift), 0, 0)

    lift = Property(float, get_lift, set_lift)

    def showEvent(self, event) -> None:  # noqa: N802
        super().showEvent(event)
        if self._started:
            return
        self._started = True
        self._start_reveal()

    def _start_reveal(self) -> None:
        lift_animation = QPropertyAnimation(self, b"lift", self)
        lift_animation.setDuration(860)
        lift_animation.setStartValue(self._lift)
        lift_animation.setEndValue(0.0)
        lift_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        sequence = QSequentialAnimationGroup(self)
        if self._delay_ms > 0:
            sequence.addPause(self._delay_ms)
        sequence.addAnimation(lift_animation)
        sequence.start()
        self._sequence = sequence


class DashboardGlassFrame(QFrame):
    """Semi-transparent dashboard glass panel. Полупрозрачная glass-панель дашборда."""

    def __init__(self, *, border_color: str = COLOR["border_default"], fill_ratio: float = 0.88) -> None:
        super().__init__()
        self._border_color = border_color
        self._fill_ratio = max(0.15, min(0.98, fill_ratio))
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        rect = QRectF(self.rect()).adjusted(1.0, 1.0, -1.0, -1.0)
        radius = float(RADIUS["xl"])

        path = QPainterPath()
        path.addRoundedRect(rect, radius, radius)

        fill_top = QColor(255, 255, 255, round(255 * self._fill_ratio))
        fill_bottom = QColor(226, 234, 243, round(255 * max(0.12, self._fill_ratio - 0.18)))
        fill_gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
        fill_gradient.setColorAt(0.0, fill_top)
        fill_gradient.setColorAt(1.0, fill_bottom)

        painter.fillPath(path, fill_gradient)
        painter.setPen(QPen(QColor(self._border_color), 1.3))
        painter.drawPath(path)

        glow_rect = QRectF(
            rect.left() + SPACING["md"],
            rect.top() + SPACING["md"],
            rect.width() * 0.46,
            rect.height() * 0.32,
        )
        glow = QRadialGradient(glow_rect.center(), max(glow_rect.width(), glow_rect.height()))
        glow.setColorAt(0.0, QColor(255, 255, 255, 78))
        glow.setColorAt(1.0, QColor(255, 255, 255, 0))
        painter.fillPath(path, glow)
        painter.end()
