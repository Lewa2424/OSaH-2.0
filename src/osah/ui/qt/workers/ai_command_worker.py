from pathlib import Path

from PySide6.QtCore import QObject, Signal

from osah.application.services.ai.resolve_user_ai_command import resolve_user_ai_command
from osah.domain.entities.ai_command_session import AiCommandSession
from osah.domain.entities.ai_conversation_context import AiConversationContext
from osah.domain.entities.ai_dialogue_state import AiDialogueState
from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.ai_ui_context import AiUiContext


class AiCommandWorker(QObject):
    """Фоновий worker для розбору AI-команди.
    Background worker for parsing an AI command.
    """

    progress = Signal(int, str)
    success = Signal(object)
    error = Signal(str)
    finished = Signal()

    def __init__(
        self,
        command_text: str,
        access_role: AccessRole,
        *,
        project_root: Path | None = None,
        prefer_fallback_model: bool = False,
        database_path: Path | None = None,
        active_session: AiCommandSession | None = None,
        conversation_context: AiConversationContext | None = None,
        dialogue_state: AiDialogueState | None = None,
        ui_context: AiUiContext | None = None,
    ) -> None:
        super().__init__()
        self._command_text = command_text
        self._access_role = access_role
        self._project_root = project_root
        self._prefer_fallback_model = prefer_fallback_model
        self._database_path = database_path
        self._active_session = active_session
        self._conversation_context = conversation_context
        self._dialogue_state = dialogue_state
        self._ui_context = ui_context

    def run(self) -> None:
        """Розбирає команду користувача у фоновому потоці.
        Parses the user command in a background thread.
        """

        try:
            self.progress.emit(20, "Розбір команди…")
            resolution = resolve_user_ai_command(
                self._command_text,
                access_role=self._access_role,
                project_root=self._project_root,
                prefer_fallback_model=self._prefer_fallback_model,
                database_path=self._database_path,
                active_session=self._active_session,
                conversation_context=self._conversation_context,
                dialogue_state=self._dialogue_state,
                ui_context=self._ui_context,
            )
            self.progress.emit(100, "Готово.")
            self.success.emit(resolution)
        except Exception as error:  # noqa: BLE001
            self.error.emit(str(error))
        finally:
            self.finished.emit()
