from pathlib import Path


# ###### ПОБУДОВА ШЛЯХУ ДО СИСТЕМНОГО ЛОГУ / ПОСТРОЕНИЕ ПУТИ К СИСТЕМНОМУ ЛОГУ ######
def build_log_file_path_from_database_path(database_path: Path) -> Path:
    """Будує шлях до системного log-файлу на основі шляху до локальної БД.
    Строит путь к системному log-файлу на основе пути к локальной БД.
    """

    return database_path.parent.parent / "logs" / "osah.log"
