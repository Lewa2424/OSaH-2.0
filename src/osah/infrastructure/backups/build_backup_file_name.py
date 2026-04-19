from datetime import datetime

from osah.domain.entities.backup_kind import BackupKind


# ###### ПОБУДОВА НАЗВИ ФАЙЛУ РЕЗЕРВНОЇ КОПІЇ / ПОСТРОЕНИЕ ИМЕНИ ФАЙЛА РЕЗЕРВНОЙ КОПИИ ######
def build_backup_file_name(backup_kind: BackupKind, created_at: datetime) -> str:
    """Повертає уніфіковану назву файлу резервної копії.
    Возвращает унифицированное имя файла резервной копии.
    """

    return f"{backup_kind.value}-{created_at.strftime('%Y%m%d-%H%M%S')}.sqlite3"
