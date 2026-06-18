from pathlib import Path

from PySide6.QtCore import QEvent, Property, QEasingCurve, QObject, QPropertyAnimation, Qt
from PySide6.QtWidgets import QWidget

from osah.application.services.ai.save_ai_drawer_tab_y_ratio import save_ai_drawer_tab_y_ratio
from osah.domain.entities.access_role import AccessRole
from osah.ui.qt.components.ai_assistant_panel import AiAssistantPanel
from osah.ui.qt.components.ai_drawer_tab import AiDrawerTab
from osah.ui.qt.components.ai_ui_metrics import AI_CONTROL_GAP, AI_DRAWER_PANEL_TAB_GAP, AI_DRAWER_PANEL_WIDTH
from osah.ui.qt.design.tokens import ANIMATION


class AiDrawerOverlay(QWidget):
    """Overlay AI-drawer поверх робочої області без стискання layout.
    Overlay AI drawer above the workspace without squeezing the main layout.
    """

    PANEL_WIDTH = AI_DRAWER_PANEL_WIDTH
    DIM_ALPHA = 0.25

    def __init__(
        self,
        host: QWidget,
        panel: AiAssistantPanel,
        *,
        tab_y_ratio: float,
        database_path: Path,
        access_role: AccessRole,
    ) -> None:
        super().__init__(host)
        self._host = host
        self._panel = panel
        self._database_path = database_path
        self._access_role = access_role
        self._tab_y_ratio = max(0.0, min(1.0, tab_y_ratio))
        self._is_open = False
        self._slide_progress = 1.0
        self._animation: QPropertyAnimation | None = None

        self._dim = QWidget(self)
        self._dim.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._dim.setStyleSheet(f"background-color: rgba(17, 24, 39, {int(255 * self.DIM_ALPHA)});")
        self._dim.hide()
        self._dim.mousePressEvent = self._on_dim_clicked  # type: ignore[method-assign]

        self._panel.setParent(self)
        self._panel.setFixedWidth(self.PANEL_WIDTH)
        self._panel.hide()

        self._tab = AiDrawerTab(self)
        self._tab.TOGGLE_REQUESTED.connect(self.toggle_drawer)
        self._tab.DRAG_POSITION_CHANGED.connect(self._on_tab_drag_position_changed)
        self._tab.DRAG_FINISHED.connect(self._on_tab_drag_finished)

        self._host.installEventFilter(self)
        self._sync_geometry()
        self.show()
        self.raise_()

    def is_open(self) -> bool:
        """Повертає True, якщо drawer відкритий.
        Returns True when the drawer is open.
        """

        return self._is_open

    def open_drawer(self) -> None:
        """Відкриває AI-drawer з анімацією.
        Opens the AI drawer with animation.
        """

        if self._is_open:
            return
        self._is_open = True
        self.setGeometry(self._host.rect())
        self._panel.show()
        self._dim.show()
        self._layout_children()
        self.raise_()
        self._animate_slide(target_progress=0.0)

    def close_drawer(self) -> None:
        """Закриває AI-drawer з анімацією.
        Closes the AI drawer with animation.
        """

        if not self._is_open:
            return
        self._is_open = False

        def _hide_layers() -> None:
            self._panel.hide()
            self._dim.hide()
            self._sync_geometry()

        self._animate_slide(target_progress=1.0, finished_callback=_hide_layers)

    def toggle_drawer(self) -> None:
        """Перемикає стан AI-drawer.
        Toggles the AI drawer open/closed state.
        """

        if self._is_open:
            self.close_drawer()
        else:
            self.open_drawer()

    def get_slide_progress(self) -> float:
        return self._slide_progress

    def set_slide_progress(self, value: float) -> None:
        self._slide_progress = max(0.0, min(1.0, value))
        self._layout_children()

    slide_progress = Property(float, get_slide_progress, set_slide_progress)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # type: ignore[override]
        if watched is self._host and event.type() == QEvent.Type.Resize:
            self._sync_geometry()
            self.raise_()
        return super().eventFilter(watched, event)

    def _on_dim_clicked(self, _event) -> None:
        self.close_drawer()

    def _on_tab_drag_position_changed(self, desired_top_y: int) -> None:
        host_top_global = self._host.mapToGlobal(self._host.rect().topLeft()).y()
        relative_top = desired_top_y - host_top_global
        min_top = AI_CONTROL_GAP
        max_top = self._host.height() - self._tab.height() - AI_CONTROL_GAP
        clamped_top = max(min_top, min(max_top, relative_top))
        available_height = max(1, self._host.height() - self._tab.height() - AI_CONTROL_GAP * 2)
        self._tab_y_ratio = (clamped_top - AI_CONTROL_GAP) / available_height
        if self._is_open:
            self._tab.move(self._tab.x(), clamped_top)
        else:
            self._apply_collapsed_geometry(clamped_top)

    def _on_tab_drag_finished(self) -> None:
        save_ai_drawer_tab_y_ratio(
            self._database_path,
            tab_y_ratio=self._tab_y_ratio,
            access_role=self._access_role,
        )

    def _sync_geometry(self) -> None:
        if self._is_open or self._slide_progress < 1.0:
            self.setGeometry(self._host.rect())
        else:
            self._apply_collapsed_geometry()
        self._layout_children()

    def _apply_collapsed_geometry(self, tab_top: int | None = None) -> None:
        host_width = self._host.width()
        host_height = self._host.height()
        if host_width <= 0 or host_height <= 0:
            return
        resolved_top = tab_top if tab_top is not None else self._resolve_tab_top_y(host_height)
        tab_x = host_width - self._tab.TAB_WIDTH
        self.setGeometry(tab_x, resolved_top, self._tab.TAB_WIDTH, self._tab.TAB_HEIGHT)

    def _layout_children(self) -> None:
        if not self._is_open and self._slide_progress >= 1.0:
            self._tab.setGeometry(0, 0, self._tab.TAB_WIDTH, self._tab.TAB_HEIGHT)
            self._dim.hide()
            self._panel.hide()
            return

        width = self.width()
        height = self.height()
        if width <= 0 or height <= 0:
            return

        self._dim.setGeometry(0, 0, width, height)

        tab_x = width - self._tab.TAB_WIDTH
        tab_y = self._resolve_tab_top_y(height)
        self._tab.setGeometry(tab_x, tab_y, self._tab.TAB_WIDTH, self._tab.TAB_HEIGHT)

        panel_x = int(
            tab_x
            - AI_DRAWER_PANEL_TAB_GAP
            - self.PANEL_WIDTH
            + self._slide_progress * self.PANEL_WIDTH
        )
        self._panel.setGeometry(panel_x, 0, self.PANEL_WIDTH, height)
        self._dim.lower()
        self._panel.raise_()
        self._tab.raise_()

    def _resolve_tab_top_y(self, height: int) -> int:
        available_height = max(1, height - self._tab.height() - AI_CONTROL_GAP * 2)
        return AI_CONTROL_GAP + int(self._tab_y_ratio * available_height)

    def _animate_slide(self, *, target_progress: float, finished_callback=None) -> None:
        if self._animation is not None:
            self._animation.stop()

        self._animation = QPropertyAnimation(self, b"slide_progress")
        self._animation.setDuration(ANIMATION["normal"])
        self._animation.setStartValue(self._slide_progress)
        self._animation.setEndValue(target_progress)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        if finished_callback is not None:
            self._animation.finished.connect(finished_callback)
        self._animation.start()
