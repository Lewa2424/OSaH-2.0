from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget

from osah.ui.qt.components.ai_ui_metrics import AI_CONTROL_BORDER, AI_CONTROL_GAP
from osah.ui.qt.components.animations.pulse import apply_pulse, stop_pulse
from osah.ui.qt.design.tokens import COLOR
from osah.ui.qt.services.format_ai_chat_message_html import format_ai_chat_message_html


class AiChatMessageRow(QWidget):
    """Рядок повідомлення чату з опційним індикатором «думаю» праворуч.
    Chat message row with an optional thinking indicator on the right.
    """

    _DOTS_FRAMES: tuple[str, ...] = ("·", "··", "···")

    def __init__(
        self,
        author: str,
        text: str,
        *,
        background: str,
        foreground: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(AI_CONTROL_GAP)

        self._bubble = QLabel(format_ai_chat_message_html(author, text))
        self._bubble.setWordWrap(True)
        self._bubble.setTextFormat(Qt.TextFormat.RichText)
        self._bubble.setStyleSheet(
            f"QLabel {{ background: {background}; color: {foreground}; border: {AI_CONTROL_BORDER} solid {COLOR['border_soft']}; "
            f"border-radius: 10px; padding: 10px; font-size: 15px; line-height: 1.4em; }}"
        )
        layout.addWidget(self._bubble, stretch=1)

        self._thinking_label = QLabel(self._DOTS_FRAMES[0])
        self._thinking_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._thinking_label.setFixedWidth(28)
        self._thinking_label.setToolTip("Обробка команди…")
        self._thinking_label.setStyleSheet(
            f"QLabel {{ color: {COLOR['text_muted']}; font-size: 20px; font-weight: 700; padding-top: 8px; }}"
        )
        self._thinking_label.hide()
        layout.addWidget(self._thinking_label, stretch=0, alignment=Qt.AlignmentFlag.AlignTop)

        self._dots_timer = QTimer(self)
        self._dots_timer.setInterval(420)
        self._dots_timer.timeout.connect(self._advance_dots_frame)
        self._dots_frame_index = 0

    def show_thinking_indicator(self) -> None:
        """Показує пульсуючий індикатор праворуч від повідомлення.
        Shows a pulsing thinking indicator to the right of the message.
        """

        self._dots_frame_index = 0
        self._thinking_label.setText(self._DOTS_FRAMES[0])
        self._thinking_label.show()
        apply_pulse(self._thinking_label, min_opacity=0.35, beat_ms=700)
        self._dots_timer.start()

    def hide_thinking_indicator(self) -> None:
        """Ховає індикатор обробки.
        Hides the processing indicator.
        """

        self._dots_timer.stop()
        stop_pulse(self._thinking_label)
        self._thinking_label.hide()

    def _advance_dots_frame(self) -> None:
        self._dots_frame_index = (self._dots_frame_index + 1) % len(self._DOTS_FRAMES)
        self._thinking_label.setText(self._DOTS_FRAMES[self._dots_frame_index])
