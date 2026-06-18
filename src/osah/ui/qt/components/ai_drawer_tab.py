from PySide6.QtCore import QPointF, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QFont, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QWidget

from osah.ui.qt.components.ai_ui_metrics import (
    AI_CONTROL_GAP,
    AI_DRAWER_TAB_BODY_WIDTH,
    AI_DRAWER_TAB_EDGE_GAP,
    AI_DRAWER_TAB_WIDTH,
)
from osah.ui.qt.design.tokens import COLOR


class AiDrawerTab(QWidget):
    """Вертикально перетягуваний ярлык AI-drawer на правому краї.
    Vertically draggable AI drawer tab on the right screen edge.
    """

    TOGGLE_REQUESTED = Signal()
    DRAG_POSITION_CHANGED = Signal(int)
    DRAG_FINISHED = Signal()

    TAB_WIDTH = AI_DRAWER_TAB_WIDTH
    TAB_HEIGHT = 88
    _DRAG_THRESHOLD_PX = 6

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedSize(self.TAB_WIDTH, self.TAB_HEIGHT)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("ClearWork AI")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._press_global_y: float | None = None
        self._dragging = False

    def paintEvent(self, _event) -> None:  # type: ignore[override]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        body_rect = QRectF(0, 0, AI_DRAWER_TAB_BODY_WIDTH, self.height())
        body = QPainterPath()
        body.addRoundedRect(body_rect, 14, 14)
        painter.fillPath(body, QColor(COLOR["accent"]))
        painter.setPen(QPen(QColor(COLOR["accent_active"]), 1))
        painter.drawPath(body)

        label_rect = QRectF(body_rect.left(), body_rect.top(), body_rect.width(), body_rect.height() / 2)
        painter.setPen(QColor(COLOR["text_on_accent"]))
        painter.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        painter.drawText(label_rect, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom, "AI")

        icon_center_y = label_rect.bottom() + AI_CONTROL_GAP + 10
        icon_center = QPointF(body_rect.center().x(), icon_center_y)
        painter.setPen(QPen(QColor(COLOR["accent_soft"]), 2))
        painter.drawLine(icon_center.x() - 5, icon_center.y(), icon_center.x() + 5, icon_center.y())
        painter.drawLine(icon_center.x(), icon_center.y() - 5, icon_center.x(), icon_center.y() + 5)
        painter.drawLine(icon_center.x() - 3, icon_center.y() - 3, icon_center.x() + 3, icon_center.y() + 3)
        painter.drawLine(icon_center.x() - 3, icon_center.y() + 3, icon_center.x() + 3, icon_center.y() - 3)

        air_rect = QRectF(AI_DRAWER_TAB_BODY_WIDTH, 0, AI_DRAWER_TAB_EDGE_GAP, self.height())
        painter.fillRect(air_rect, Qt.GlobalColor.transparent)

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        if event.button() == Qt.MouseButton.LeftButton:
            self._press_global_y = event.globalPosition().y()
            self._dragging = False
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:  # type: ignore[override]
        if self._press_global_y is None:
            return
        delta_y = event.globalPosition().y() - self._press_global_y
        if not self._dragging and abs(delta_y) > self._DRAG_THRESHOLD_PX:
            self._dragging = True
            self.setCursor(Qt.CursorShape.SizeVerCursor)
        if self._dragging:
            self.DRAG_POSITION_CHANGED.emit(int(event.globalPosition().y() - self.height() / 2))
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:  # type: ignore[override]
        if event.button() == Qt.MouseButton.LeftButton and self._press_global_y is not None:
            if self._dragging:
                self.DRAG_FINISHED.emit()
            else:
                self.TOGGLE_REQUESTED.emit()
        self._press_global_y = None
        self._dragging = False
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        super().mouseReleaseEvent(event)
