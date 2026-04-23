from collections.abc import Callable

from PySide6.QtCore import QObject, Signal


class WorkspaceReloadWorker(QObject):
    """Background worker for heavy workspace reloading operations."""

    progress = Signal(int, str)
    success = Signal(object)
    error = Signal(str)
    finished = Signal()

    def __init__(self, load_callable: Callable[[], object], operation_label: str) -> None:
        super().__init__()
        self._load_callable = load_callable
        self._operation_label = operation_label

    # ###### ФОНОВЕ ПЕРЕЗАВАНТАЖЕННЯ WORKSPACE / BACKGROUND WORKSPACE RELOAD ######
    def run(self) -> None:
        """Executes workspace loading outside UI thread."""

        try:
            self.progress.emit(5, f"{self._operation_label}: запуск.")
            result = self._load_callable()
            self.progress.emit(100, f"{self._operation_label}: завершено.")
            self.success.emit(result)
        except Exception as error:  # noqa: BLE001
            self.error.emit(f"{self._operation_label}: {error}")
        finally:
            self.finished.emit()
