"""
NavFillPushButton — nav-кнопка з сегментною діаграмою фону.
NavFillPushButton — nav button with a segmented background diagram.
"""
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QColor, QFont, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QPushButton, QStyle, QStyleOptionButton

from osah.domain.services.nav_fill_constants import SEGMENT_COUNT
from osah.ui.qt.design.tokens import COLOR, FONT, RADIUS
from osah.ui.qt.design.ui_scale import scaled_px


class NavFillPushButton(QPushButton):
    """QPushButton, що малює 120-сегментну палітру замість плоского alert-фону.
    QPushButton that paints a 120-segment palette instead of a flat alert background.
    """

    def __init__(self, text: str) -> None:
        super().__init__(text)
        self._fill_colors: tuple[str, ...] | None = None
        self._problem_border = False
        self.setMouseTracking(True)

    def set_fill_colors(self, colors: tuple[str, ...] | None) -> None:
        """Оновлює палітру сегментів діаграми.
        Updates the diagram segment palette.
        """

        self._fill_colors = colors
        self.update()

    def enterEvent(self, event) -> None:
        super().enterEvent(event)
        if self._fill_colors is not None and not self.isChecked():
            self.update()

    def leaveEvent(self, event) -> None:
        super().leaveEvent(event)
        if self._fill_colors is not None and not self.isChecked():
            self.update()

    def set_problem_border(self, enabled: bool) -> None:
        """Вмикає червону рамку для критичних розділів.
        Enables a red border for critical sections.
        """

        if self._problem_border != enabled:
            self._problem_border = enabled
            self.update()

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        option = QStyleOptionButton()
        self.initStyleOption(option)
        rect = QRectF(self.rect())

        if self.isChecked() or self._fill_colors is None:
            self.style().drawControl(QStyle.ControlElement.CE_PushButton, option, painter, self)
            return

        radius = scaled_px(RADIUS["md"])
        clip_path = QPainterPath()
        clip_path.addRoundedRect(rect, radius, radius)
        painter.setClipPath(clip_path)

        segment_width = rect.width() / SEGMENT_COUNT
        for index, hex_color in enumerate(self._fill_colors):
            painter.fillRect(
                QRectF(index * segment_width, rect.top(), segment_width + 0.5, rect.height()),
                QColor(hex_color),
            )

        if self.underMouse():
            painter.fillRect(rect, QColor(0, 0, 0, 20))
        if option.state & QStyle.StateFlag.State_Sunken:
            painter.fillRect(rect, QColor(0, 0, 0, 35))

        painter.setClipping(False)
        border_color = COLOR["nav_item_problem_border"] if self._problem_border else COLOR["border_default"]
        border_width = 2 if self._problem_border else 1
        painter.setPen(QPen(QColor(border_color), border_width))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        inset = border_width / 2
        painter.drawRoundedRect(
            rect.adjusted(inset, inset, -inset, -inset),
            radius,
            radius,
        )

        painter.setPen(QColor(COLOR["nav_item_text"]))
        label_font = QFont(FONT["nav_item"][0], scaled_px(FONT["nav_item"][1]))
        label_font.setBold(True)
        painter.setFont(label_font)
        text_rect = rect.adjusted(scaled_px(12), 0, -scaled_px(8), 0)
        painter.drawText(
            text_rect.toRect(),
            int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter),
            self.text(),
        )
