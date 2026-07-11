from dataclasses import dataclass
from enum import StrEnum
from typing import Literal

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStyle,
    QVBoxLayout,
    QWidget,
)

from osah.ui.qt.design.tokens import COLOR, RADIUS, SPACING


class AppDialogIcon(StrEnum):
    """Compact app dialog icon kind. / Тип іконки компактного діалогу."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    QUESTION = "question"


@dataclass(frozen=True)
class AppDialogAction:
    """Compact app dialog button action. / Кнопка компактного діалогу."""

    action_id: str
    label: str
    variant: Literal["accent", "secondary", "danger"] = "accent"


_ICON_PIXMAP: dict[AppDialogIcon, QStyle.StandardPixmap] = {
    AppDialogIcon.INFO: QStyle.StandardPixmap.SP_MessageBoxInformation,
    AppDialogIcon.WARNING: QStyle.StandardPixmap.SP_MessageBoxWarning,
    AppDialogIcon.CRITICAL: QStyle.StandardPixmap.SP_MessageBoxCritical,
    AppDialogIcon.QUESTION: QStyle.StandardPixmap.SP_MessageBoxQuestion,
}

_ICON_TONE: dict[AppDialogIcon, tuple[str, str]] = {
    AppDialogIcon.INFO: (COLOR["info_bg"], COLOR["news_accent"]),
    AppDialogIcon.WARNING: (COLOR["warning_subtle"], COLOR["warning"]),
    AppDialogIcon.CRITICAL: (COLOR["critical_subtle"], COLOR["critical"]),
    AppDialogIcon.QUESTION: (COLOR["accent_subtle"], COLOR["accent"]),
}


class AppDialog(QDialog):
    """Compact modal dialog in ClearWork visual style. / Компактний модальний діалог у стилі ClearWork."""

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
        self._icon = icon

        self.setWindowTitle(window_title)
        self.setModal(True)
        self.setFixedWidth(460)
        self.setStyleSheet(
            f"""
            QDialog {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #F8FBFD, stop:1 #EFF4F9);
                color: {COLOR['text_primary']};
            }}
            QFrame#dialogSurface {{
                background: rgba(255, 255, 255, 0.97);
                border: 1px solid #D9E2EC;
                border-radius: {RADIUS['xxl']}px;
            }}
            QLabel#dialogTitle {{
                color: {COLOR['text_primary']};
                font-size: 18px;
                font-weight: 900;
            }}
            QLabel#dialogDetail {{
                color: {COLOR['text_secondary']};
                font-size: 14px;
                font-weight: 600;
            }}
            QPushButton {{
                min-height: 40px;
                padding: 0 18px;
                border-radius: {RADIUS['lg']}px;
                font-size: 14px;
                font-weight: 800;
            }}
            """
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(SPACING["xl"], SPACING["xl"], SPACING["xl"], SPACING["xl"])
        root.setSpacing(0)

        surface = QFrame()
        surface.setObjectName("dialogSurface")
        root.addWidget(surface)

        surface_layout = QVBoxLayout(surface)
        surface_layout.setContentsMargins(SPACING["xl"], SPACING["xl"], SPACING["xl"], SPACING["xl"])
        surface_layout.setSpacing(SPACING["lg"])
        surface_layout.addWidget(self._build_message_row(message, detail, icon))
        surface_layout.addLayout(self._build_buttons(actions, default_action_id, button_layout))

    def selected_action_id(self) -> str:
        """Returns the identifier of the clicked action. / Повертає ідентифікатор натиснутої дії."""

        return self._selected_action_id

    def _build_message_row(self, message: str, detail: str | None, icon: AppDialogIcon) -> QWidget:
        background, foreground = _ICON_TONE[icon]

        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING["md"])

        icon_wrap = QFrame()
        icon_wrap.setFixedSize(56, 56)
        icon_wrap.setStyleSheet(
            f"background: {background}; border-radius: 18px; border: 1px solid {background};"
        )
        icon_layout = QVBoxLayout(icon_wrap)
        icon_layout.setContentsMargins(0, 0, 0, 0)

        icon_label = QLabel()
        icon_label.setPixmap(self.style().standardIcon(_ICON_PIXMAP[icon]).pixmap(26, 26))
        icon_label.setFixedSize(56, 56)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet(f"color: {foreground};")
        icon_layout.addWidget(icon_label)
        layout.addWidget(icon_wrap, alignment=Qt.AlignmentFlag.AlignTop)

        text_column = QVBoxLayout()
        text_column.setContentsMargins(0, 0, 0, 0)
        text_column.setSpacing(SPACING["xs"])

        message_label = QLabel(message)
        message_label.setObjectName("dialogTitle")
        message_label.setWordWrap(True)
        message_font = QFont(message_label.font())
        message_font.setBold(True)
        message_font.setPixelSize(18)
        message_label.setFont(message_font)
        text_column.addWidget(message_label)

        if detail and detail.strip():
            detail_label = QLabel(detail.strip())
            detail_label.setObjectName("dialogDetail")
            detail_label.setWordWrap(True)
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
        if action.variant == "danger":
            button.setStyleSheet(
                f"""
                QPushButton {{
                    background: {COLOR['critical_subtle']};
                    color: {COLOR['critical']};
                    border: 1px solid #F0BBBB;
                }}
                QPushButton:hover {{
                    background: #F8D7D7;
                }}
                """
            )
        button.setAutoDefault(action.action_id == default_action_id)
        button.setDefault(action.action_id == default_action_id)
        button.clicked.connect(lambda _checked=False, action_id=action.action_id: self._accept_action(action_id))
        return button

    def _accept_action(self, action_id: str) -> None:
        self._selected_action_id = action_id
        self.accept()


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
    """Shows a compact dialog and returns the selected action identifier. / Показує компактний діалог."""

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
    """Shows a compact confirmation dialog and returns True when confirmed. / Показує компактне підтвердження."""

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
