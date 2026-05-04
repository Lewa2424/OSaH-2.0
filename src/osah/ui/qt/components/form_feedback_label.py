from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QLabel

from osah.ui.qt.design.tokens import COLOR, RADIUS


class FormFeedbackLabel(QLabel):
    """Світлий inline-блок результату дії у формі.
    Light inline feedback block for form action results.
    """

    def __init__(self) -> None:
        super().__init__("")
        self.setWordWrap(True)
        self.setVisible(False)
        self._message_token = 0

    # ###### ПОКАЗ УСПІХУ / SHOW SUCCESS ######
    def show_success(self, message: str) -> None:
        """Показує не модальне повідомлення про успішне збереження.
        Shows a non-modal success message after saving.
        """

        self._show_message(message, COLOR["success_subtle"], COLOR["success"])

    # ###### ПОКАЗ ПОМИЛКИ / SHOW ERROR ######
    def show_error(self, message: str) -> None:
        """Показує не модальне повідомлення про помилку валідації.
        Shows a non-modal validation error message.
        """

        self._show_message(message, COLOR["critical_subtle"], COLOR["critical"])

    # ###### ВІДОБРАЖЕННЯ ПОВІДОМЛЕННЯ / SHOW MESSAGE ######
    def _show_message(self, message: str, background: str, foreground: str) -> None:
        """Оновлює текст і стиль feedback-блоку.
        Updates feedback block text and style.
        """

        self._message_token += 1
        current_token = self._message_token
        self.setText(message)
        self.setStyleSheet(
            f"background: {background}; color: {foreground}; border: 1px solid {foreground}; "
            f"border-radius: {RADIUS['md']}px; padding: 8px 10px; font-weight: 800;"
        )
        self.setVisible(True)
        QTimer.singleShot(6000, lambda: self._hide_if_current(current_token))

    def _hide_if_current(self, message_token: int) -> None:
        """Приховує повідомлення, якщо за цей час його не було замінено.
        Hides the message if it has not been replaced in the meantime.
        """

        if message_token == self._message_token:
            self.clear()
            self.setVisible(False)
