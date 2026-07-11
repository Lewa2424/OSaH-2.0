from pathlib import Path

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QAbstractScrollArea, QHBoxLayout, QPushButton, QScrollBar, QVBoxLayout, QWidget

from osah.ui.qt.design.tokens import COLOR, SPACING


_ICON_DIR = Path(__file__).resolve().parents[1] / "assets" / "icons"


class ScrollableHorizontalFrame(QWidget):
    """Обгортка з верхнім горизонтальним scrollbar для довгого контенту.
    Wrapper with a top horizontal scrollbar for long content.
    """

    def __init__(self, content_widget: QAbstractScrollArea) -> None:
        super().__init__()
        self._content_widget = content_widget
        self._is_syncing = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING["xs"])

        controls = QWidget()
        controls.setObjectName("contentScrollControls")
        controls_layout = QHBoxLayout(controls)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(SPACING["sm"])

        self._left_button = self._create_scroll_button("left")
        self._left_button.clicked.connect(self._scroll_left)
        controls_layout.addWidget(self._left_button)

        self._top_scrollbar = QScrollBar(Qt.Orientation.Horizontal)
        self._top_scrollbar.setObjectName("contentTopScrollBar")
        self._top_scrollbar.setMinimumHeight(12)
        self._top_scrollbar.setStyleSheet(_build_scrollbar_style())
        self._top_scrollbar.valueChanged.connect(self._sync_content_scrollbar)
        controls_layout.addWidget(self._top_scrollbar, stretch=1)

        self._right_button = self._create_scroll_button("right")
        self._right_button.clicked.connect(self._scroll_right)
        controls_layout.addWidget(self._right_button)

        layout.addWidget(controls)
        layout.addWidget(self._content_widget, stretch=1)

        native_scrollbar = self._content_widget.horizontalScrollBar()
        native_scrollbar.setMinimumHeight(11)
        native_scrollbar.setStyleSheet(_build_scrollbar_style())
        native_scrollbar.rangeChanged.connect(self._sync_top_range)
        native_scrollbar.valueChanged.connect(self._sync_top_value)
        self._sync_top_range(native_scrollbar.minimum(), native_scrollbar.maximum())
        self._sync_top_value(native_scrollbar.value())

    def content_widget(self) -> QAbstractScrollArea:
        """Повертає вкладений scrollable-віджет.
        Returns the wrapped scrollable widget.
        """

        return self._content_widget

    def _create_scroll_button(self, direction: str) -> QPushButton:
        button = QPushButton()
        button.setFixedSize(28, 28)
        button.setIcon(_build_scroll_icon(direction))
        button.setIconSize(QSize(22, 22))
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setObjectName("contentScrollButton")
        button.setStyleSheet(_build_scroll_button_style())
        return button

    def _sync_top_range(self, minimum: int, maximum: int) -> None:
        self._top_scrollbar.setRange(minimum, maximum)
        self._top_scrollbar.setPageStep(self._content_widget.horizontalScrollBar().pageStep())
        self._update_button_state()

    def _sync_top_value(self, value: int) -> None:
        if self._is_syncing:
            return
        self._is_syncing = True
        self._top_scrollbar.setValue(value)
        self._is_syncing = False
        self._update_button_state()

    def _sync_content_scrollbar(self, value: int) -> None:
        if self._is_syncing:
            return
        self._is_syncing = True
        self._content_widget.horizontalScrollBar().setValue(value)
        self._is_syncing = False
        self._update_button_state()

    def _scroll_left(self) -> None:
        scrollbar = self._content_widget.horizontalScrollBar()
        scrollbar.setValue(max(scrollbar.minimum(), scrollbar.value() - max(120, scrollbar.pageStep())))

    def _scroll_right(self) -> None:
        scrollbar = self._content_widget.horizontalScrollBar()
        scrollbar.setValue(min(scrollbar.maximum(), scrollbar.value() + max(120, scrollbar.pageStep())))

    def _update_button_state(self) -> None:
        scrollbar = self._content_widget.horizontalScrollBar()
        self._left_button.setEnabled(scrollbar.value() > scrollbar.minimum())
        self._right_button.setEnabled(scrollbar.value() < scrollbar.maximum())


def _build_scrollbar_style() -> str:
    return (
        f"QScrollBar:horizontal {{ background: {COLOR['bg_panel']}; height: 11px; border-radius: 5px; }}"
        f"QScrollBar::handle:horizontal {{ background: {COLOR['accent']}; border-radius: 5px; min-width: 48px; }}"
        f"QScrollBar::handle:horizontal:hover {{ background: {COLOR['accent_hover']}; }}"
        "QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0px; }"
        "QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal { background: transparent; }"
    )


def _build_scroll_button_style() -> str:
    return (
        f"QPushButton#contentScrollButton {{ background: {COLOR['text_primary']}; color: {COLOR['text_on_accent']}; "
        f"border: 1px solid {COLOR['text_primary']}; border-radius: 14px; padding: 0px; }}"
        f"QPushButton#contentScrollButton:hover {{ background: {COLOR['accent_hover']}; border-color: {COLOR['accent_hover']}; }}"
        f"QPushButton#contentScrollButton:pressed {{ background: {COLOR['accent_active']}; }}"
        f"QPushButton#contentScrollButton:disabled {{ background: {COLOR['bg_panel']}; color: {COLOR['text_muted']}; "
        f"border: 1px solid {COLOR['border_soft']}; }}"
    )


def _build_scroll_icon(direction: str) -> QIcon:
    icon = QIcon()
    icon.addFile(str(_ICON_DIR / f"chevron_{direction}_white.svg"), QSize(22, 22), QIcon.Mode.Normal)
    icon.addFile(str(_ICON_DIR / f"chevron_{direction}_muted.svg"), QSize(22, 22), QIcon.Mode.Disabled)
    return icon
