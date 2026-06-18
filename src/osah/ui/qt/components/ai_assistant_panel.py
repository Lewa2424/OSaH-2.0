from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget

from osah.domain.entities.ai_entity_choice import AiEntityChoice
from osah.ui.qt.components.ai_chat_message_row import AiChatMessageRow
from osah.ui.qt.components.ai_command_input import AiCommandInput
from osah.ui.qt.components.ai_ui_metrics import (
    AI_CONTROL_BORDER,
    AI_CONTROL_GAP,
    AI_DRAWER_PANEL_WIDTH,
    AI_PANEL_CLOSE_SIZE,
    AI_THINKING_INDICATOR_DELAY_MS,
)
from osah.ui.qt.design.tokens import COLOR, FONT, SPACING


class AiAssistantPanel(QFrame):
    """Права панель AI-помічника з короткою історією.
    Right-side AI assistant panel with short message history.
    """

    entity_choice_selected = Signal(str)
    panel_close_requested = Signal()
    command_submitted = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedWidth(AI_DRAWER_PANEL_WIDTH)
        self.setStyleSheet(
            f"QFrame {{ background: {COLOR['bg_card']}; border-left: 1px solid {COLOR['border_soft']}; "
            f"border-top: none; border-right: none; border-bottom: none; }}"
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(SPACING["md"], SPACING["md"], SPACING["md"], SPACING["md"])
        root.setSpacing(AI_CONTROL_GAP)

        header = QHBoxLayout()
        header.setSpacing(AI_CONTROL_GAP)
        left_spacer = QWidget()
        left_spacer.setFixedSize(AI_PANEL_CLOSE_SIZE, AI_PANEL_CLOSE_SIZE)
        header.addWidget(left_spacer)
        title = QLabel("ClearWork AI")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont(FONT["title_l"][0], 36, QFont.Bold))
        header.addWidget(title, stretch=1)
        close_button = QPushButton("×")
        close_button.setFixedSize(AI_PANEL_CLOSE_SIZE, AI_PANEL_CLOSE_SIZE)
        close_button.setStyleSheet(
            f"QPushButton {{ background: {COLOR['bg_workspace']}; color: {COLOR['text_secondary']}; "
            f"border: {AI_CONTROL_BORDER} solid {COLOR['border_soft']}; border-radius: 8px; "
            f"font-size: 16px; font-weight: 700; padding: 0; }}"
            f"QPushButton:hover {{ background: {COLOR['button_secondary_hover']}; }}"
        )
        close_button.clicked.connect(self.panel_close_requested.emit)
        header.addWidget(close_button)
        root.addLayout(header)

        self._status_label = QLabel("Готовий до команд.")
        self._status_label.setWordWrap(True)
        self._status_label.setStyleSheet(
            f"color: {COLOR['text_muted']}; font-size: 15px; line-height: 1.35em;"
        )
        root.addWidget(self._status_label)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._messages_host = QWidget()
        self._messages_layout = QVBoxLayout(self._messages_host)
        self._messages_layout.setContentsMargins(0, 0, 0, 0)
        self._messages_layout.setSpacing(AI_CONTROL_GAP)
        self._messages_layout.addStretch()
        self._scroll.setWidget(self._messages_host)
        root.addWidget(self._scroll, stretch=1)

        self._choices_host = QWidget()
        self._choices_layout = QVBoxLayout(self._choices_host)
        self._choices_layout.setContentsMargins(0, 0, 0, 0)
        self._choices_layout.setSpacing(AI_CONTROL_GAP)
        self._choices_host.hide()
        root.addWidget(self._choices_host)

        self._follow_up_host = QWidget()
        self._follow_up_layout = QVBoxLayout(self._follow_up_host)
        self._follow_up_layout.setContentsMargins(0, 0, 0, 0)
        self._follow_up_layout.setSpacing(AI_CONTROL_GAP)
        self._follow_up_host.hide()
        root.addWidget(self._follow_up_host)

        self._command_input = AiCommandInput(self, panel_mode=True)
        self._command_input.command_submitted.connect(self.command_submitted.emit)
        root.addWidget(self._command_input)

        self._thinking_delay_timer = QTimer(self)
        self._thinking_delay_timer.setSingleShot(True)
        self._thinking_delay_timer.timeout.connect(self._show_delayed_thinking_indicator)
        self._processing_message_row: AiChatMessageRow | None = None

    def focus_command_input(self) -> None:
        """Переводить фокус у поле команди панелі.
        Moves focus to the panel command input field.
        """

        self._command_input.focus_input()

    def set_command_input_enabled(self, enabled: bool) -> None:
        """Вмикає або вимикає поле команди панелі.
        Enables or disables the panel command input field.
        """

        self._command_input.set_enabled(enabled)

    def set_busy(self, busy: bool, message: str = "Думаю…") -> None:
        """Показує або ховає стан обробки команди.
        Shows or hides command processing state.
        """

        self._status_label.setText(message if busy else "Готовий до команд.")
        if busy:
            self._schedule_thinking_indicator()
            return
        self._clear_thinking_indicator()

    def append_user_message(self, text: str) -> None:
        """Додає повідомлення користувача до історії.
        Appends a user message to the short history.
        """

        row = self._append_message("Ви", text, COLOR["accent_soft"], COLOR["text_primary"])
        self._processing_message_row = row

    def append_assistant_message(self, text: str) -> None:
        """Додає відповідь помічника до історії.
        Appends an assistant message to the short history.
        """

        self._append_message("AI", text, COLOR["bg_workspace"], COLOR["text_primary"])

    def show_entity_choices(
        self,
        choices: tuple[AiEntityChoice, ...],
        *,
        prompt: str | None = None,
    ) -> None:
        """Показує варіанти для уточнення сутності.
        Shows entity choices for clarification.
        """

        self._clear_choices()
        if not choices:
            self._choices_host.hide()
            return

        if prompt:
            prompt_label = QLabel(prompt)
            prompt_label.setWordWrap(True)
            prompt_label.setStyleSheet(f"font-size: 15px; color: {COLOR['text_primary']};")
            self._choices_layout.addWidget(prompt_label)
        for choice in choices:
            button = QPushButton(choice.label)
            button.setStyleSheet(
                f"QPushButton {{ text-align: left; padding: 8px 10px; border: {AI_CONTROL_BORDER} solid {COLOR['border_soft']}; "
                f"border-radius: 8px; background: {COLOR['bg_workspace']}; font-size: 14px; }}"
            )
            button.clicked.connect(lambda _checked=False, choice_id=choice.choice_id: self.entity_choice_selected.emit(choice_id))
            self._choices_layout.addWidget(button)
        self._choices_host.show()

    def clear_entity_choices(self) -> None:
        """Прибирає блок уточнення сутностей.
        Clears the entity clarification block.
        """

        self._clear_choices()
        self._choices_host.hide()

    def show_follow_up_action(self, label: str, callback) -> None:
        """Показує додаткову дію після текстової відповіді AI.
        Shows an extra action button after an AI text answer.
        """

        self._clear_follow_up()
        button = QPushButton(label)
        button.setStyleSheet(
            f"QPushButton {{ text-align: left; padding: 8px 10px; border: {AI_CONTROL_BORDER} solid {COLOR['accent']}; "
            f"border-radius: 8px; background: {COLOR['accent_soft']}; color: {COLOR['text_primary']}; font-size: 14px; }}"
        )
        button.clicked.connect(callback)
        self._follow_up_layout.addWidget(button)
        self._follow_up_host.show()

    def _clear_follow_up(self) -> None:
        while self._follow_up_layout.count():
            item = self._follow_up_layout.takeAt(0)
            if widget := item.widget():
                widget.deleteLater()
        self._follow_up_host.hide()

    def _append_message(self, author: str, text: str, background: str, foreground: str) -> AiChatMessageRow:
        row = AiChatMessageRow(author, text, background=background, foreground=foreground)
        insert_index = max(0, self._messages_layout.count() - 1)
        self._messages_layout.insertWidget(insert_index, row)
        QTimer.singleShot(0, self._scroll_to_bottom)
        return row

    def _scroll_to_bottom(self) -> None:
        """Прокручує історію чату до останнього повідомлення.
        Scrolls chat history to the latest message.
        """

        scrollbar = self._scroll.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _schedule_thinking_indicator(self) -> None:
        """Запускає таймер показу індикатора, якщо обробка триває довше порогу.
        Starts a timer to show the indicator when processing exceeds the threshold.
        """

        if self._processing_message_row is None:
            return
        if self._thinking_delay_timer.isActive():
            return
        self._thinking_delay_timer.start(AI_THINKING_INDICATOR_DELAY_MS)

    def _show_delayed_thinking_indicator(self) -> None:
        if self._processing_message_row is not None:
            self._processing_message_row.show_thinking_indicator()

    def _clear_thinking_indicator(self) -> None:
        self._thinking_delay_timer.stop()
        if self._processing_message_row is not None:
            self._processing_message_row.hide_thinking_indicator()
            self._processing_message_row = None

    def _clear_choices(self) -> None:
        while self._choices_layout.count():
            item = self._choices_layout.takeAt(0)
            if widget := item.widget():
                widget.deleteLater()
