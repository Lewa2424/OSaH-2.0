from pathlib import Path

from osah.domain.entities.backup_snapshot import BackupSnapshot
from osah.infrastructure.backups.parse_backup_snapshot_from_path import parse_backup_snapshot_from_path


# ###### ЧИТАННЯ СПИСКУ РЕЗЕРВНИХ КОПІЙ З КАТАЛОГУ / ЧТЕНИЕ СПИСКА РЕЗЕРВНЫХ КОПИЙ ИЗ КАТАЛОГА ######
def list_backup_snapshots_from_directory(backup_directory_path: Path) -> tuple[BackupSnapshot, ...]:
    """Повертає список резервних копій з каталогу у зворотному хронологічному порядку.
    Возвращает список резервных копий из каталога в обратном хронологическом порядке.
    """

    if not backup_directory_path.exists():
        return ()

    backup_snapshots: list[BackupSnapshot] = []
    for backup_file_path in sorted(backup_directory_path.glob("*.sqlite3"), reverse=True):
        backup_snapshot = parse_backup_snapshot_from_path(backup_file_path)
        if backup_snapshot is not None:
            backup_snapshots.append(backup_snapshot)
    return tuple(backup_snapshots)
