import re
from pathlib import Path

from osah.domain.entities.backup_kind import BackupKind
from osah.domain.entities.backup_snapshot import BackupSnapshot


# ###### РОЗБІР ОПИСУ РЕЗЕРВНОЇ КОПІЇ З ФАЙЛУ / РАЗБОР ОПИСАНИЯ РЕЗЕРВНОЙ КОПИИ ИЗ ФАЙЛА ######
def parse_backup_snapshot_from_path(backup_file_path: Path) -> BackupSnapshot | None:
    """Повертає опис резервної копії з імені файлу або None для стороннього файлу.
    Возвращает описание резервной копии из имени файла или None для стороннего файла.
    """

    match = re.match(r"^(manual|auto|safety)-(\d{8})-(\d{6})\.sqlite3$", backup_file_path.name)
    if match is None:
        return None

    backup_kind = BackupKind(match.group(1))
    created_at_text = f"{match.group(2)[0:4]}-{match.group(2)[4:6]}-{match.group(2)[6:8]} {match.group(3)[0:2]}:{match.group(3)[2:4]}:{match.group(3)[4:6]}"
    return BackupSnapshot(
        file_name=backup_file_path.name,
        file_path=backup_file_path,
        backup_kind=backup_kind,
        created_at_text=created_at_text,
        size_bytes=backup_file_path.stat().st_size,
    )
