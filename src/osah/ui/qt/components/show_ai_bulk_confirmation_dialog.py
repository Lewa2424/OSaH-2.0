from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from osah.domain.entities.ai_bulk_confirmation_view import AiBulkConfirmationView
from osah.ui.qt.components.app_dialog import AppDialogIcon, _ICON_PIXMAP
from osah.ui.qt.design.tokens import COLOR, SPACING


@dataclass(slots=True, frozen=True)
class AiBulkConfirmationDialogResult:
    """Результат діалогу підтвердження масової AI-дії.
    Result of the bulk AI confirmation dialog.
    """

    action_id: str


def show_ai_bulk_confirmation_dialog(
    parent: QWidget,
    view: AiBulkConfirmationView,
) -> AiBulkConfirmationDialogResult:
    """Показує діалог підтвердження масової AI-дії зі списком працівників.
    Shows the bulk AI confirmation dialog with the employee list.
    """

    dialog = QDialog(parent)
    dialog.setWindowTitle(view.title)
    dialog.setModal(True)
    dialog.setMinimumWidth(520)
    dialog.setMinimumHeight(360)
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

    action_label = QLabel(view.action_summary)
    action_label.setWordWrap(True)
    action_label.setStyleSheet(f"color: {COLOR['text_secondary']}; font-size: 13px;")
    root.addWidget(action_label)

    if view.warning_text:
        warning_label = QLabel(view.warning_text)
        warning_label.setWordWrap(True)
        warning_label.setStyleSheet(f"color: {COLOR['warning']}; font-size: 12px;")
        root.addWidget(warning_label)

    table = QTableWidget(len(view.rows), 3)
    table.setHorizontalHeaderLabels(["ПІБ", "Таб. №", "Попередження"])
    table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
    table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
    table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
    table.verticalHeader().setVisible(False)
    table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
    for row_index, row in enumerate(view.rows):
        table.setItem(row_index, 0, QTableWidgetItem(row.full_name))
        table.setItem(row_index, 1, QTableWidgetItem(row.personnel_number))
        table.setItem(row_index, 2, QTableWidgetItem(row.warning_text))
    root.addWidget(table, stretch=1)

    buttons = QHBoxLayout()
    buttons.addStretch()
    cancel_button = QPushButton("Скасувати")
    confirm_button = QPushButton("Підтвердити")
    confirm_button.setDefault(True)
    buttons.addWidget(cancel_button)
    buttons.addWidget(confirm_button)
    root.addLayout(buttons)

    selected_action = "cancel"

    def on_cancel() -> None:
        nonlocal selected_action
        selected_action = "cancel"
        dialog.reject()

    def on_confirm() -> None:
        nonlocal selected_action
        selected_action = "confirm"
        dialog.accept()

    cancel_button.clicked.connect(on_cancel)
    confirm_button.clicked.connect(on_confirm)
    dialog.exec()
    return AiBulkConfirmationDialogResult(action_id=selected_action)
