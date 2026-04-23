from PySide6.QtCore import QObject, QThread, Signal


class WorkerTaskController(QObject):
    """Controls one background worker task at a time."""

    started = Signal()
    progress = Signal(int, str)
    success = Signal(object)
    error = Signal(str)
    finished = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._thread: QThread | None = None
        self._worker: QObject | None = None

    # ###### СТАН ФОНОВОЇ ЗАДАЧІ / BACKGROUND TASK STATE ######
    def is_busy(self) -> bool:
        """Returns whether background task is currently running."""

        return self._thread is not None and self._thread.isRunning()

    # ###### ЗАПУСК ФОНОВОЇ ЗАДАЧІ / START BACKGROUND TASK ######
    def start_worker(self, worker: QObject) -> bool:
        """Starts worker in a dedicated QThread if controller is idle."""

        if self.is_busy():
            return False

        thread = QThread()
        self._thread = thread
        self._worker = worker
        worker.moveToThread(thread)

        thread.started.connect(worker.run)  # type: ignore[attr-defined]
        worker.progress.connect(self.progress.emit)  # type: ignore[attr-defined]
        worker.success.connect(self.success.emit)  # type: ignore[attr-defined]
        worker.error.connect(self.error.emit)  # type: ignore[attr-defined]
        worker.finished.connect(thread.quit)  # type: ignore[attr-defined]
        worker.finished.connect(self._cleanup_after_finish)  # type: ignore[attr-defined]
        thread.finished.connect(thread.deleteLater)

        thread.start()
        self.started.emit()
        return True

    # ###### ЗАВЕРШЕННЯ І ПРИБИРАННЯ / FINISH AND CLEANUP ######
    def _cleanup_after_finish(self) -> None:
        """Clears worker/thread references after task finish."""

        self._worker = None
        self._thread = None
        self.finished.emit()
