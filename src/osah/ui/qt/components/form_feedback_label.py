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

        self.setText(message)
        self.setStyleSheet(
            f"background: {background}; color: {foreground}; border: 1px solid {foreground}; "
            f"border-radius: {RADIUS['md']}px; padding: 8px 10px; font-weight: 800;"
        )
        self.setVisible(True)
