from pathlib import Path


# ###### ПАПКА ЕКСПОРТУ ПОРТ-Р / PORT-R EXPORTS DIRECTORY ######
def build_port_r_exports_directory(project_root: Path) -> Path:
    """Повертає шлях до папки експорту документів ПОРТ-Р у корені застосунку.
    Возвращает путь к папке экспорта документов ПОРТ-Р в корне приложения.
    """

    exports_directory = project_root / "exports" / "port_r"
    exports_directory.mkdir(parents=True, exist_ok=True)
    return exports_directory
