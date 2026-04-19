from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class ApplicationPaths:
    """Шляхи зберігання робочих даних застосунку.
    Пути хранения рабочих данных приложения.
    """

    project_root: Path
    data_directory: Path
    log_directory: Path
    database_file_path: Path
    log_file_path: Path


# ###### ПОБУДОВА ШЛЯХІВ ЗАСТОСУНКУ / ПОСТРОЕНИЕ ПУТЕЙ ПРИЛОЖЕНИЯ ######
def build_application_paths(project_root: Path | None = None) -> ApplicationPaths:
    """Будує всі основні шляхи зберігання для локального застосунку.
    Строит все основные пути хранения для локального приложения.
    """

    resolved_root = project_root or Path(__file__).resolve().parents[4]
    data_directory = resolved_root / "data"
    log_directory = resolved_root / "logs"
    return ApplicationPaths(
        project_root=resolved_root,
        data_directory=data_directory,
        log_directory=log_directory,
        database_file_path=data_directory / "osah.sqlite3",
        log_file_path=log_directory / "osah.log",
    )
