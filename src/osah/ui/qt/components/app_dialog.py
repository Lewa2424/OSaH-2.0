from dataclasses import dataclass
from enum import StrEnum
from typing import Literal

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStyle,
    QVBoxLayout,
    QWidget,
)

from osah.ui.qt.design.tokens import COLOR, SPACING


class AppDialogIcon(StrEnum):
    """Тип іконки компактного діалогу / Compact app dialog icon kind."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    QUESTION = "question"


@dataclass(frozen=True)
class AppDialogAction:
    """Кнопка компактного діалогу / Compact app dialog button action."""

    action_id: str
    label: str
    variant: Literal["accent", "secondary", "danger"] = "accent"


_ICON_PIXMAP: dict[AppDialogIcon, QStyle.StandardPixmap] = {
    AppDialogIcon.INFO: QStyle.StandardPixmap.SP_MessageBoxInformation,
    AppDialogIcon.WARNING: QStyle.StandardPixmap.SP_MessageBoxWarning,
    AppDialogIcon.CRITICAL: QStyle.StandardPixmap.SP_MessageBoxCritical,
    AppDialogIcon.QUESTION: QStyle.StandardPixmap.SP_MessageBoxQuestion,
}


class AppDialog(QDialog):
    """Компактний модальний діалог у стилі ClearWork.
    Compact modal dialog in ClearWork visual style.
    """

    def __init__(
        self,
        parent: QWidget | None,
        *,
        window_title: str,
        message: str,
        detail: str | None,
        icon: AppDialogIcon,
        actions: tuple[AppDialogAction, ...],
        default_action_id: str,
        button_layout: Literal["row", "stacked"] = "row",
    ) -> None:
        super().__init__(parent)
        self._selected_action_id = default_action_id

        self.setWindowTitle(window_title)
        self.setModal(True)
        self.setFixedWidth(380)
        self.setStyleSheet(
            f"QDialog {{ background: {COLOR['bg_card']}; color: {COLOR['text_primary']}; "
            f"border: 1px solid {COLOR['card_border']}; }}"
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(SPACING["lg"], SPACING["md"], SPACING["lg"], SPACING["md"])
        root.setSpacing(SPACING["md"])
        root.addWidget(self._build_message_row(message, detail, icon))
        root.addLayout(self._build_buttons(actions, default_action_id, button_layout))

    def selected_action_id(self) -> str:
        """Повертає ідентифікатор натиснутої дії.
        Returns the identifier of the clicked action.
        """

        return self._selected_action_id

    def _build_message_row(self, message: str, detail: str | None, icon: AppDialogIcon) -> QWidget:
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING["sm"])

        icon_label = QLabel()
        icon_label.setPixmap(self.style().standardIcon(_ICON_PIXMAP[icon]).pixmap(28, 28))
        icon_label.setFixedSize(28, 28)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(icon_label)

        text_column = QVBoxLayout()
        text_column.setContentsMargins(0, 0, 0, 0)
        text_column.setSpacing(SPACING["xs"])

        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_font = QFont(message_label.font())
        message_font.setBold(True)
        message_font.setPixelSize(14)
        message_label.setFont(message_font)
        message_label.setStyleSheet(f"color: {COLOR['text_primary']};")
        text_column.addWidget(message_label)

        if detail and detail.strip():
            detail_label = QLabel(detail.strip())
            detail_label.setWordWrap(True)
            detail_label.setStyleSheet(f"color: {COLOR['text_secondary']}; font-size: 13px;")
            text_column.addWidget(detail_label)

        layout.addLayout(text_column, stretch=1)
        return row

    def _build_buttons(
        self,
        actions: tuple[AppDialogAction, ...],
        default_action_id: str,
        button_layout: Literal["row", "stacked"],
    ) -> QVBoxLayout:
        buttons_root = QVBoxLayout()
        buttons_root.setSpacing(SPACING["sm"])

        if button_layout == "stacked":
            primary_action = actions[0]
            buttons_root.addWidget(self._create_button(primary_action, default_action_id))
            if len(actions) > 1:
                secondary_row = QHBoxLayout()
                secondary_row.setSpacing(SPACING["sm"])
                for action in actions[1:]:
                    secondary_row.addWidget(self._create_button(action, default_action_id))
                buttons_root.addLayout(secondary_row)
            return buttons_root

        buttons_row = QHBoxLayout()
        buttons_row.setSpacing(SPACING["sm"])
        buttons_row.addStretch()
        for action in actions:
            buttons_row.addWidget(self._create_button(action, default_action_id))
        buttons_root.addLayout(buttons_row)
        return buttons_root

    def _create_button(self, action: AppDialogAction, default_action_id: str) -> QPushButton:
        button = QPushButton(action.label)
        button.setProperty("variant", action.variant)
        button.setAutoDefault(action.action_id == default_action_id)
        button.setDefault(action.action_id == default_action_id)
        button.clicked.connect(lambda _checked=False, action_id=action.action_id: self._accept_action(action_id))
        return button

    def _accept_action(self, action_id: str) -> None:
        self._selected_action_id = action_id
        self.accept()


# ###### ПОКАЗ КОМПАКТНОГО ДІАЛОГУ / SHOW COMPACT APP DIALOG ######
def show_app_dialog(
    parent: QWidget | None,
    *,
    window_title: str,
    message: str,
    detail: str | None = None,
    icon: AppDialogIcon = AppDialogIcon.INFO,
    actions: tuple[AppDialogAction, ...] = (AppDialogAction("ok", "OK", "accent"),),
    default_action_id: str = "ok",
    button_layout: Literal["row", "stacked"] = "row",
) -> str:
    """Показує компактний діалог і повертає ідентифікатор обраної дії.
    Shows a compact dialog and returns the selected action identifier.
    """

    dialog = AppDialog(
        parent,
        window_title=window_title,
        message=message,
        detail=detail,
        icon=icon,
        actions=actions,
        default_action_id=default_action_id,
        button_layout=button_layout,
    )
    dialog.exec()
    return dialog.selected_action_id()


# ###### ПІДТВЕРДЖЕННЯ ДІЇ / SHOW APP CONFIRM DIALOG ######
def show_app_confirm_dialog(
    parent: QWidget | None,
    window_title: str,
    message: str,
    *,
    detail: str | None = None,
    icon: AppDialogIcon = AppDialogIcon.QUESTION,
    confirm_label: str = "Так",
    cancel_label: str = "Скасувати",
    destructive: bool = False,
    default_confirm: bool = False,
) -> bool:
    """Показує компактне підтвердження і повертає True, якщо дію підтверджено.
    Shows a compact confirmation dialog and returns True when confirmed.
    """

    confirm_variant: Literal["accent", "secondary", "danger"] = "danger" if destructive else "accent"
    selected_action_id = show_app_dialog(
        parent,
        window_title=window_title,
        message=message,
        detail=detail,
        icon=icon,
        actions=(
            AppDialogAction("cancel", cancel_label, "secondary"),
            AppDialogAction("confirm", confirm_label, confirm_variant),
        ),
        default_action_id="confirm" if default_confirm else "cancel",
    )
    return selected_action_id == "confirm"
