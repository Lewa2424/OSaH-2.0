from PySide6.QtWidgets import QMessageBox, QPushButton, QWidget

from osah.ui.qt.design.tokens import COLOR


# ###### ДІАЛОГ НАГАДУВАННЯ ПРО ЩОДЕННИЙ ЗВІТ / SHOW MANUAL REPORT PROMPT DIALOG ######
def show_manual_report_prompt_dialog(parent: QWidget | None) -> str:
    """Показує стилізований діалог нагадування про щоденний звіт і повертає вибір користувача.
    Shows a styled daily report reminder dialog and returns the user's choice.
    """

    message_box = QMessageBox(parent)
    message_box.setIcon(QMessageBox.Icon.Question)
    message_box.setWindowTitle("Щоденний звіт")
    message_box.setText("Настав час сформувати щоденний звіт. Сформувати файл звіту зараз?")

    build_button = message_box.addButton("Так, сформувати", QMessageBox.ButtonRole.AcceptRole)
    remind_later_button = message_box.addButton("Нагадати пізніше", QMessageBox.ButtonRole.ActionRole)
    skip_today_button = message_box.addButton("Пропустити сьогодні", QMessageBox.ButtonRole.DestructiveRole)
    message_box.setDefaultButton(build_button)
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
            min-width: 132px;
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

    clicked_button = message_box.clickedButton()
    if clicked_button is build_button:
        return "build"
    if clicked_button is skip_today_button:
        return "skip"
    if clicked_button is remind_later_button:
        return "later"
    return "later"
