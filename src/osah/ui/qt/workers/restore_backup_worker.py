from pathlib import Path

from PySide6.QtCore import QObject, Signal

from osah.application.services.restore_backup_snapshot import restore_backup_snapshot


class RestoreBackupWorker(QObject):
    """Background worker for restore-from-backup operation."""

    progress = Signal(int, str)
    success = Signal(object)
    error = Signal(str)
    finished = Signal()

    def __init__(self, database_path: Path, backup_file_path: Path) -> None:
        super().__init__()
        self._database_path = database_path
        self._backup_file_path = backup_file_path

    # ###### ФОНОВЕ ВІДНОВЛЕННЯ З БЕКАПУ / BACKGROUND RESTORE FROM BACKUP ######
    def run(self) -> None:
        """Restores system state from selected backup file."""

        try:
            self.progress.emit(10, "Підготовка до відновлення з резервної копії.")
            safety_backup_path = restore_backup_snapshot(self._database_path, self._backup_file_path)
            self.progress.emit(100, "Відновлення завершено.")
            self.success.emit({"restored_from": self._backup_file_path, "safety_copy": safety_backup_path})
        except Exception as error:  # noqa: BLE001
            self.error.emit(f"Не вдалося виконати відновлення: {error}")
        finally:
            self.finished.emit()
