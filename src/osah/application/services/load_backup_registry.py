from pathlib import Path

from osah.domain.entities.backup_snapshot import BackupSnapshot
from osah.infrastructure.backups.build_backup_directory_path import build_backup_directory_path
from osah.infrastructure.backups.list_backup_snapshots_from_directory import list_backup_snapshots_from_directory


# ###### ЗАВАНТАЖЕННЯ РЕЄСТРУ РЕЗЕРВНИХ КОПІЙ / ЗАГРУЗКА РЕЕСТРА РЕЗЕРВНЫХ КОПИЙ ######
def load_backup_registry(database_path: Path) -> tuple[BackupSnapshot, ...]:
    """Повертає список резервних копій локальної системи.
    Возвращает список резервных копий локальной системы.
    """

    return list_backup_snapshots_from_directory(build_backup_directory_path(database_path))
