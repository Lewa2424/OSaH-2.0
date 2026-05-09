from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox, QWidget

from osah.ui.qt.design.tokens import COLOR


# ###### ПОКАЗ СТИЛІЗОВАНОГО MESSAGE BOX / ПОКАЗ СТИЛИЗОВАННОГО MESSAGE BOX ######
def show_styled_message_box(
    parent: QWidget | None,
    title_text: str,
    body_text: str,
    icon: QMessageBox.Icon,
    standard_buttons: QMessageBox.StandardButton,
    default_button: QMessageBox.StandardButton,
) -> QMessageBox.StandardButton:
    """Показує QMessageBox у стилі OSaH та повертає натиснуту стандартну кнопку.
    Показывает QMessageBox в стиле OSaH и возвращает нажатую стандартную кнопку.
    """

    message_box = QMessageBox(parent)
    message_box.setIcon(icon)
    message_box.setWindowTitle(title_text)
    message_box.setText(body_text)
    message_box.setStandardButtons(standard_buttons)
    message_box.setDefaultButton(default_button)
    message_box.setTextFormat(Qt.TextFormat.PlainText)
    message_box.setStyleSheet(
        f"""
        QMessageBox {{
            background: {COLOR['bg_card']};
        }}
        QMessageBox QLabel {{
            color: {COLOR['text_primary']};
            font-size: 14px;
            margin-bottom: 10px;
            min-width: 360px;
        }}
        QMessageBox QPushButton {{
            min-width: 112px;
            padding: 8px 16px;
            font-weight: 700;
            border-radius: 8px;
            color: {COLOR['button_secondary_text']};
            background: {COLOR['button_secondary_bg']};
            border: 1px solid {COLOR['button_secondary_border']};
        }}
        QMessageBox QPushButton:hover {{
            background: {COLOR['button_secondary_hover']};
        }}
        QMessageBox QPushButton:pressed {{
            background: {COLOR['button_secondary_active']};
        }}
        """
    )
    message_box.exec()
    return message_box.standardButton(message_box.clickedButton())
