from pathlib import Path

from PySide6.QtCore import QObject, Signal

from osah.application.services.create_backup_snapshot import create_backup_snapshot
from osah.domain.entities.backup_kind import BackupKind


class BackupCreateWorker(QObject):
    """Background worker for manual backup creation."""

    progress = Signal(int, str)
    success = Signal(object)
    error = Signal(str)
    finished = Signal()

    def __init__(self, database_path: Path, backup_kind: BackupKind = BackupKind.MANUAL) -> None:
        super().__init__()
        self._database_path = database_path
        self._backup_kind = backup_kind

    # ###### ФОНОВЕ СТВОРЕННЯ БЕКАПУ / BACKGROUND BACKUP CREATION ######
    def run(self) -> None:
        """Creates backup snapshot outside UI thread."""

        try:
            self.progress.emit(15, "Створення резервної копії запущено.")
            backup_path = create_backup_snapshot(self._database_path, self._backup_kind)
            self.progress.emit(100, "Резервну копію створено.")
            self.success.emit(backup_path)
        except Exception as error:  # noqa: BLE001
            self.error.emit(f"Не вдалося створити резервну копію: {error}")
        finally:
            self.finished.emit()
