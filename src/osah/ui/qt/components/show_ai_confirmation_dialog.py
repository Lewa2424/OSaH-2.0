from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QCheckBox, QDialog, QHBoxLayout, QLabel, QPushButton, QStyle, QVBoxLayout, QWidget

from osah.domain.entities.ai_confirmation_view import AiConfirmationView
from osah.ui.qt.components.app_dialog import AppDialogIcon, _ICON_PIXMAP
from osah.ui.qt.design.tokens import COLOR, SPACING


@dataclass(slots=True, frozen=True)
class AiSynonymOffer:
    """Пропозиція зберегти синонім ЗІЗ.
    Offer to remember a PPE synonym mapping.
    """

    source_phrase: str
    target_value: str


@dataclass(slots=True, frozen=True)
class AiConfirmationDialogResult:
    """Результат діалогу підтвердження AI-дії.
    Result of the AI confirmation dialog.
    """

    action_id: str
    remember_synonym: bool = False


def show_ai_confirmation_dialog(
    parent: QWidget,
    view: AiConfirmationView,
    *,
    synonym_offer: AiSynonymOffer | None = None,
) -> AiConfirmationDialogResult:
    """Показує діалог підтвердження AI-дії.
    Shows the AI action confirmation dialog.
    """

    dialog = QDialog(parent)
    dialog.setWindowTitle(view.title)
    dialog.setModal(True)
    dialog.setFixedWidth(420)
    dialog.setStyleSheet(
        f"QDialog {{ background: {COLOR['bg_card']}; color: {COLOR['text_primary']}; "
        f"border: 1px solid {COLOR['card_border']}; }}"
    )

    root = QVBoxLayout(dialog)
    root.setContentsMargins(SPACING["lg"], SPACING["md"], SPACING["lg"], SPACING["md"])
    root.setSpacing(SPACING["md"])

    header = QHBoxLayout()
    icon_label = QLabel()
    icon_label.setPixmap(dialog.style().standardIcon(_ICON_PIXMAP[AppDialogIcon.QUESTION]).pixmap(28, 28))
    header.addWidget(icon_label)
    message_label = QLabel(view.summary)
    message_label.setWordWrap(True)
    message_font = QFont(message_label.font())
    message_font.setBold(True)
    message_font.setPixelSize(14)
    message_label.setFont(message_font)
    header.addWidget(message_label, stretch=1)
    root.addLayout(header)

    detail_lines = [f"{line.label}: {line.value}" for line in view.lines]
    if view.warning_text:
        detail_lines.append("")
        detail_lines.append(view.warning_text)
    if detail_lines:
        detail_label = QLabel("\n".join(detail_lines))
        detail_label.setWordWrap(True)
        detail_label.setStyleSheet(f"color: {COLOR['text_secondary']}; font-size: 13px;")
        root.addWidget(detail_label)

    remember_checkbox: QCheckBox | None = None
    if synonym_offer is not None:
        remember_checkbox = QCheckBox(
            f"Запам'ятати синонім: «{synonym_offer.source_phrase}» → «{synonym_offer.target_value}»"
        )
        remember_checkbox.setStyleSheet(f"color: {COLOR['text_secondary']};")
        root.addWidget(remember_checkbox)

    buttons_row = QHBoxLayout()
    buttons_row.setSpacing(SPACING["sm"])
    selected_action_id = "cancel"

    def _accept(action_id: str) -> None:
        nonlocal selected_action_id
        selected_action_id = action_id
        dialog.accept()

    confirm_button = QPushButton("Підтвердити і записати")
    confirm_button.clicked.connect(lambda: _accept("confirm"))
    cancel_button = QPushButton("Скасувати")
    cancel_button.clicked.connect(lambda: _accept("cancel"))
    buttons_row.addWidget(confirm_button)
    buttons_row.addWidget(cancel_button)
    root.addLayout(buttons_row)

    dialog.exec()
    return AiConfirmationDialogResult(
        action_id=selected_action_id,
        remember_synonym=bool(remember_checkbox is not None and remember_checkbox.isChecked()),
    )
