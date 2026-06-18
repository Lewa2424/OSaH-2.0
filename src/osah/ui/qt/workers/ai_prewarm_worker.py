from pathlib import Path

from PySide6.QtCore import QObject, Signal

from osah.infrastructure.ai.llama_server_session import ensure_llama_server_running
from osah.infrastructure.config.build_ai_runtime_paths import build_ai_runtime_paths, resolve_active_ai_model_path


class AiPrewarmWorker(QObject):
    """Фоновий worker для попереднього запуску llama-server.
    Background worker that prewarms llama-server after login.
    """

    progress = Signal(int, str)
    success = Signal(object)
    error = Signal(str)
    finished = Signal()

    def __init__(self, project_root: Path) -> None:
        super().__init__()
        self._project_root = project_root

    def run(self) -> None:
        """Запускає llama-server у фоні, якщо runtime доступний.
        Starts llama-server in the background when runtime is available.
        """

        try:
            self.progress.emit(10, "Підготовка локального AI…")
            runtime_paths = build_ai_runtime_paths(self._project_root)
            model_path = resolve_active_ai_model_path(runtime_paths)
            ensure_llama_server_running(runtime_paths, model_path)
            self.success.emit(True)
        except Exception as error:  # noqa: BLE001
            self.error.emit(str(error))
        finally:
            self.finished.emit()
