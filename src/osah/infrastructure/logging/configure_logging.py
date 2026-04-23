import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from osah.infrastructure.logging.purge_old_log_files import purge_old_log_files
from osah.infrastructure.logging.sanitize_log_message import sanitize_log_message


# ###### НАЛАШТУВАННЯ ЛОГУВАННЯ / LOGGING CONFIGURATION ######
def configure_logging(
    log_file_path: Path,
    max_bytes: int = 1_000_000,
    backup_count: int = 5,
    retention_days: int = 30,
) -> None:
    """Налаштовує файлове логування з ротацією та політикою зберігання.
    Configures file logging with rotation and retention policy.
    """

    log_file_path.parent.mkdir(parents=True, exist_ok=True)
    purge_old_log_files(log_file_path.parent, retention_days=retention_days)
    file_handler = RotatingFileHandler(
        log_file_path,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    file_handler.addFilter(_SensitiveLogFilter())
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[file_handler],
        force=True,
    )


class _SensitiveLogFilter(logging.Filter):
    """Фільтр файлового handler, який маскує секрети навіть при прямому logging API.
    File handler filter that redacts secrets even when code uses the raw logging API.
    """

    # ###### ФІЛЬТРАЦІЯ ЛОГ-ЗАПИСУ / LOG RECORD FILTER ######
    def filter(self, record: logging.LogRecord) -> bool:
        """Оновлює текст log-record перед форматуванням.
        Updates log-record text before formatting.
        """

        record.msg = sanitize_log_message(record.getMessage())
        record.args = ()
        return True
