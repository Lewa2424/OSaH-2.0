from pathlib import Path


# ###### ПОБУДОВА ШЛЯХУ RECOVERY-ФАЙЛУ / ПОСТРОЕНИЕ ПУТИ RECOVERY-ФАЙЛА ######
def build_recovery_file_path(database_path: Path, installation_id: str) -> Path:
    """Будує шлях до recovery-файлу в локальному каталозі застосунку.
    Строит путь к recovery-файлу в локальном каталоге приложения.
    """

    return database_path.parent / "recovery" / f"recovery-{installation_id}.txt"
