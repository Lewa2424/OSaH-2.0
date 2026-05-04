from PySide6.QtCore import QDate, QPoint, Qt
from PySide6.QtGui import QKeyEvent, QMouseEvent, QResizeEvent
from PySide6.QtWidgets import QCalendarWidget, QFrame, QLineEdit, QToolButton, QVBoxLayout

from osah.ui.qt.design.tokens import COLOR, RADIUS


class _CalendarPopup(QFrame):
    """Контекстне popup-вікно з календарем для вибору дати.
    Context popup window with a calendar for date selection.
    """

    def __init__(self, owner: "DateLineEdit") -> None:
        super().__init__(owner, Qt.WindowType.Popup)
        self._owner = owner
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet(
            f"""
            QFrame {{
                background: {COLOR["bg_card"]};
                border: 1px solid {COLOR["border_default"]};
                border-radius: {RADIUS["md"]}px;
            }}
            QCalendarWidget {{
                background: {COLOR["bg_card"]};
                color: {COLOR["text_primary"]};
                border: none;
            }}
            QCalendarWidget QWidget#qt_calendar_navigationbar {{
                background: {COLOR["bg_panel"]};
                border-bottom: 1px solid {COLOR["border_soft"]};
            }}
            QCalendarWidget QToolButton {{
                background: transparent;
                color: {COLOR["text_primary"]};
                border: none;
                padding: 6px 10px;
                font-weight: 700;
            }}
            QCalendarWidget QToolButton:hover {{
                background: {COLOR["hover_bg"]};
                border-radius: {RADIUS["sm"]}px;
            }}
            QCalendarWidget QMenu {{
                background: {COLOR["bg_card"]};
                color: {COLOR["text_primary"]};
                border: 1px solid {COLOR["border_default"]};
            }}
            QCalendarWidget QSpinBox {{
                background: {COLOR["bg_card"]};
                color: {COLOR["text_primary"]};
                border: 1px solid {COLOR["input_border"]};
                border-radius: {RADIUS["sm"]}px;
                padding: 4px 6px;
            }}
            QCalendarWidget QAbstractItemView:enabled {{
                background: {COLOR["bg_card"]};
                color: {COLOR["text_primary"]};
                selection-background-color: {COLOR["accent_soft"]};
                selection-color: {COLOR["text_primary"]};
                alternate-background-color: {COLOR["table_row_alt_bg"]};
            }}
            QCalendarWidget QAbstractItemView:disabled {{
                color: {COLOR["text_muted"]};
            }}
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        self.calendar = QCalendarWidget(self)
        self.calendar.setGridVisible(True)
        self.calendar.clicked.connect(self._apply_selected_date)
        self.calendar.activated.connect(self._apply_selected_date)
        layout.addWidget(self.calendar)

    def open_for_owner(self) -> None:
        """Відкриває popup під полем із попередньо вибраною датою.
        Opens the popup below the field with a preselected date.
        """

        selected_date = self._owner.selected_date_or_today()
        self.calendar.setSelectedDate(selected_date)
        self.calendar.setCurrentPage(selected_date.year(), selected_date.month())
        self.move(self._owner.mapToGlobal(QPoint(0, self._owner.height())))
        self.show()
        self.raise_()
        self.activateWindow()

    def _apply_selected_date(self, selected_date: QDate) -> None:
        self._owner.setText(selected_date.toString("dd.MM.yyyy"))
        self.close()
        self._owner.setFocus()


class DateLineEdit(QLineEdit):
    """Поле дати з popup-календарем та збереженим ручним введенням.
    Date field with a popup calendar while preserving manual input.
    """

    def __init__(self) -> None:
        super().__init__()
        self._calendar_popup = _CalendarPopup(self)
        self._calendar_button = QToolButton(self)
        self._calendar_button.setCursor(Qt.CursorShape.ArrowCursor)
        self._calendar_button.setText("v")
        self._calendar_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._calendar_button.clicked.connect(self._open_calendar_popup)
        self.setTextMargins(0, 0, 26, 0)
        self.setStyleSheet(
            f"""
            QLineEdit {{
                padding-right: 28px;
            }}
            QToolButton {{
                border: none;
                background: transparent;
                color: {COLOR["accent"]};
                font-weight: 700;
            }}
            QToolButton:hover {{
                color: {COLOR["accent_hover"]};
            }}
            """
        )

    def mousePressEvent(self, event: QMouseEvent) -> None:  # type: ignore[override]
        super().mousePressEvent(event)
        if event.button() == Qt.MouseButton.MiddleButton and not self.isReadOnly():
            self._open_calendar_popup()

    def resizeEvent(self, event: QResizeEvent) -> None:  # type: ignore[override]
        super().resizeEvent(event)
        button_width = 24
        frame_width = 4
        self._calendar_button.setGeometry(
            self.width() - button_width - frame_width,
            frame_width,
            button_width,
            max(18, self.height() - frame_width * 2),
        )

    def keyPressEvent(self, event: QKeyEvent) -> None:  # type: ignore[override]
        if event.key() == Qt.Key.Key_Down and event.modifiers() & Qt.KeyboardModifier.AltModifier:
            self._open_calendar_popup()
            return
        super().keyPressEvent(event)

    def selected_date_or_today(self) -> QDate:
        """Повертає дату з поля або поточну системну дату.
        Returns the field date or the current system date.
        """

        selected_date = QDate.fromString(self.text().strip(), "dd.MM.yyyy")
        return selected_date if selected_date.isValid() else QDate.currentDate()

    def _open_calendar_popup(self) -> None:
        if self.isReadOnly() or not self.isEnabled():
            return
        self._calendar_popup.open_for_owner()

    def clear(self) -> None:  # type: ignore[override]
        """Очищає поле та скидає popup-календар до системної дати.
        Clears the field and resets the popup calendar to the system date.
        """

        super().clear()
        self._calendar_popup.calendar.setSelectedDate(QDate.currentDate())
        self._calendar_popup.calendar.setCurrentPage(QDate.currentDate().year(), QDate.currentDate().month())
