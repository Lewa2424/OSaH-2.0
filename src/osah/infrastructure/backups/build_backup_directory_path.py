from pathlib import Path


# ###### ПОБУДОВА ШЛЯХУ КАТАЛОГУ РЕЗЕРВНИХ КОПІЙ / ПОСТРОЕНИЕ ПУТИ КАТАЛОГА РЕЗЕРВНЫХ КОПИЙ ######
def build_backup_directory_path(database_path: Path) -> Path:
    """Повертає каталог зберігання резервних копій для поточної локальної БД.
    Возвращает каталог хранения резервных копий для текущей локальной БД.
    """

    return database_path.parent / "backups"
