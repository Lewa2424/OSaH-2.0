import logging
from pathlib import Path


# ###### НАЛАШТУВАННЯ ЛОГУВАННЯ / НАСТРОЙКА ЛОГИРОВАНИЯ ######
def configure_logging(log_file_path: Path) -> None:
    """Налаштовує файлове логування для локального застосунку.
    Настраивает файловое логирование для локального приложения.
    """

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[logging.FileHandler(log_file_path, encoding="utf-8")],
        force=True,
    )
