import math
from dataclasses import dataclass

from PySide6.QtCore import QEvent, QObject, QRectF, QTimer, Qt
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPen, QRadialGradient
from PySide6.QtWidgets import QWidget


@dataclass(frozen=True)
class AmbientTheme:
    base_top: str
    base_mid: str
    base_bottom: str
    orb_a: tuple[int, int, int, int]
    orb_b: tuple[int, int, int, int]
    orb_c: tuple[int, int, int, int]
    sweep: tuple[int, int, int, int]
    grid_minor: tuple[int, int, int, int]
    grid_major: tuple[int, int, int, int]


_THEMES: dict[str, AmbientTheme] = {
    "operations": AmbientTheme("#EEF3F8", "#D7E0EA", "#F8FBFD", (58, 95, 138, 72), (6, 105, 196, 52), (252, 173, 15, 36), (255, 255, 255, 44), (17, 24, 39, 11), (17, 24, 39, 18)),
    "trainings": AmbientTheme("#F4F8FF", "#E1EBF6", "#FCFDFE", (42, 92, 168, 76), (255, 165, 38, 42), (203, 64, 66, 30), (255, 255, 255, 40), (25, 48, 87, 10), (25, 48, 87, 18)),
    "ppe": AmbientTheme("#F1FBF7", "#DDF1E7", "#FBFDFC", (7, 181, 81, 62), (22, 163, 74, 44), (58, 95, 138, 24), (255, 255, 255, 38), (15, 76, 48, 9), (15, 76, 48, 16)),
    "medical": AmbientTheme("#F2FAFD", "#DDECF2", "#FBFEFF", (6, 105, 196, 60), (0, 168, 181, 40), (252, 173, 15, 18), (255, 255, 255, 36), (12, 70, 89, 10), (12, 70, 89, 16)),
    "permits": AmbientTheme("#FFF6F3", "#F6E4DE", "#FFFDFC", (181, 16, 16, 52), (252, 173, 15, 44), (58, 95, 138, 24), (255, 255, 255, 36), (93, 31, 25, 10), (93, 31, 25, 16)),
    "contractors": AmbientTheme("#F4F8FC", "#E0E9F2", "#FCFDFC", (58, 95, 138, 60), (7, 181, 81, 30), (252, 173, 15, 18), (255, 255, 255, 38), (18, 42, 71, 10), (18, 42, 71, 16)),
    "archive": AmbientTheme("#F5F7FB", "#E5E9F1", "#FCFCFE", (103, 92, 161, 44), (58, 95, 138, 40), (139, 149, 165, 30), (255, 255, 255, 34), (34, 46, 62, 10), (34, 46, 62, 16)),
    "reports": AmbientTheme("#F7FAFD", "#E3ECF5", "#FFFFFF", (6, 105, 196, 56), (252, 173, 15, 32), (58, 95, 138, 24), (255, 255, 255, 40), (17, 36, 64, 10), (17, 36, 64, 17)),
    "news": AmbientTheme("#F3F8FF", "#E1ECFA", "#FCFEFF", (6, 105, 196, 62), (58, 95, 138, 34), (7, 181, 81, 18), (255, 255, 255, 42), (16, 44, 84, 10), (16, 44, 84, 17)),
    "settings": AmbientTheme("#F4F7FB", "#E1E8F1", "#FCFDFE", (58, 95, 138, 52), (6, 105, 196, 34), (139, 149, 165, 20), (255, 255, 255, 34), (23, 37, 58, 10), (23, 37, 58, 16)),
    "about": AmbientTheme("#F7FAFD", "#E8EEF5", "#FFFEFC", (58, 95, 138, 46), (252, 173, 15, 34), (6, 105, 196, 20), (255, 255, 255, 34), (24, 38, 63, 9), (24, 38, 63, 15)),
    "port": AmbientTheme("#F2F6FB", "#DDE6F0", "#FBFDFE", (32, 71, 120, 64), (0, 132, 145, 32), (219, 136, 55, 24), (255, 255, 255, 38), (20, 41, 67, 10), (20, 41, 67, 18)),
}


class _BackgroundResizeFilter(QObject):
    def __init__(self, parent_widget: QWidget, background_widget: QWidget) -> None:
        super().__init__(parent_widget)
        self._parent_widget = parent_widget
        self._background_widget = background_widget

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        if watched is self._parent_widget and event.type() in {QEvent.Type.Resize, QEvent.Type.Show, QEvent.Type.LayoutRequest}:
            self._background_widget.setGeometry(self._parent_widget.rect())
            self._background_widget.lower()
        return super().eventFilter(watched, event)


class AmbientSectionBackground(QWidget):
    """Painter-based animated background for operational screens.
    Анімований painter-фон для службових екранів.
    """

    def __init__(self, parent: QWidget, theme_name: str) -> None:
        super().__init__(parent)
        self._theme_name = theme_name
        self._phase = 0.0
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAutoFillBackground(False)

        self._timer = QTimer(self)
        self._timer.setInterval(33)
        self._timer.timeout.connect(self._advance_phase)
        self._timer.start()

    def set_theme(self, theme_name: str) -> None:
        self._theme_name = theme_name
        self.update()

    def _advance_phase(self) -> None:
        self._phase = (self._phase + 0.006) % 1.0
        self.update()

    def paintEvent(self, _event) -> None:  # noqa: N802
        theme = _THEMES.get(self._theme_name, _THEMES["operations"])
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        rect = QRectF(self.rect())
        base_gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
        base_gradient.setColorAt(0.0, QColor(theme.base_top))
        base_gradient.setColorAt(0.48, QColor(theme.base_mid))
        base_gradient.setColorAt(1.0, QColor(theme.base_bottom))
        painter.fillRect(rect, base_gradient)

        self._paint_orb(
            painter,
            rect,
            center_x=rect.width() * (0.14 + 0.08 * self._phase),
            center_y=rect.height() * 0.12,
            radius=max(rect.width(), rect.height()) * 0.28,
            inner=QColor(*theme.orb_a),
        )
        self._paint_orb(
            painter,
            rect,
            center_x=rect.width() * 0.82,
            center_y=rect.height() * (0.26 + 0.10 * (1.0 - self._phase)),
            radius=max(rect.width(), rect.height()) * 0.24,
            inner=QColor(*theme.orb_b),
        )
        self._paint_orb(
            painter,
            rect,
            center_x=rect.width() * (0.55 + 0.04 * math.sin(self._phase * math.pi * 2.0)),
            center_y=rect.height() * 0.82,
            radius=max(rect.width(), rect.height()) * 0.20,
            inner=QColor(*theme.orb_c),
        )

        self._paint_grid(painter, rect, theme)
        self._paint_sweep(painter, rect, theme)
        painter.end()

    def _paint_orb(
        self,
        painter: QPainter,
        rect: QRectF,
        *,
        center_x: float,
        center_y: float,
        radius: float,
        inner: QColor,
    ) -> None:
        gradient = QRadialGradient(center_x, center_y, radius)
        outer = QColor(inner)
        outer.setAlpha(0)
        gradient.setColorAt(0.0, inner)
        gradient.setColorAt(1.0, outer)
        painter.fillRect(rect, gradient)

    def _paint_grid(self, painter: QPainter, rect: QRectF, theme: AmbientTheme) -> None:
        minor_pen = QPen(QColor(*theme.grid_minor), 1)
        major_pen = QPen(QColor(*theme.grid_major), 1)
        x_step = 36
        y_step = 28
        for x_pos in range(0, int(rect.width()), x_step):
            painter.setPen(major_pen if x_pos % (x_step * 4) == 0 else minor_pen)
            painter.drawLine(x_pos, 0, x_pos, int(rect.height()))
        for y_pos in range(0, int(rect.height()), y_step):
            painter.setPen(major_pen if y_pos % (y_step * 4) == 0 else minor_pen)
            painter.drawLine(0, y_pos, int(rect.width()), y_pos)

    def _paint_sweep(self, painter: QPainter, rect: QRectF, theme: AmbientTheme) -> None:
        sweep_width = max(140.0, rect.width() * 0.16)
        x_pos = -sweep_width + (rect.width() + sweep_width * 2.0) * self._phase
        sweep = QColor(*theme.sweep)
        gradient = QLinearGradient(x_pos, 0, x_pos + sweep_width, 0)
        gradient.setColorAt(0.0, QColor(sweep.red(), sweep.green(), sweep.blue(), 0))
        gradient.setColorAt(0.42, QColor(sweep.red(), sweep.green(), sweep.blue(), 0))
        gradient.setColorAt(0.50, sweep)
        gradient.setColorAt(0.58, QColor(sweep.red(), sweep.green(), sweep.blue(), 0))
        gradient.setColorAt(1.0, QColor(sweep.red(), sweep.green(), sweep.blue(), 0))
        painter.fillRect(rect, gradient)


def install_ambient_background(
    widget: QWidget,
    object_name: str,
    *,
    theme: str = "operations",
    extra_rules: str = "",
) -> None:
    """Installs a themed animated painter background on a screen widget.
    Встановлює тематичний анімований painter-фон для екрана.
    """

    widget.setObjectName(object_name)
    background_layer = getattr(widget, "_ambient_background_layer", None)
    if isinstance(background_layer, AmbientSectionBackground):
        background_layer.set_theme(theme)
        background_layer.setGeometry(widget.rect())
        background_layer.lower()
    else:
        background_layer = AmbientSectionBackground(widget, theme)
        background_layer.setGeometry(widget.rect())
        background_layer.lower()
        widget._ambient_background_layer = background_layer  # type: ignore[attr-defined]
        resize_filter = _BackgroundResizeFilter(widget, background_layer)
        widget._ambient_background_resize_filter = resize_filter  # type: ignore[attr-defined]
        widget.installEventFilter(resize_filter)
        background_layer.show()

    widget.setStyleSheet(
        f"""
        QWidget#{object_name} {{
            background: transparent;
        }}
        {extra_rules}
        """
    )
