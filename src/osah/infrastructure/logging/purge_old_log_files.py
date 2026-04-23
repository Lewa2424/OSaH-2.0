import time
from pathlib import Path


# ###### ВИДАЛЕННЯ СТАРИХ ЛОГІВ / OLD LOG FILE PURGE ######
def purge_old_log_files(log_directory_path: Path, retention_days: int = 30) -> None:
    """Видаляє старі log-файли за політикою зберігання.
    Deletes old log files according to the retention policy.
    """

    if retention_days <= 0 or not log_directory_path.exists():
        return

    cutoff_timestamp = time.time() - retention_days * 24 * 60 * 60
    for log_file_path in log_directory_path.glob("*.log*"):
        try:
            if log_file_path.stat().st_mtime < cutoff_timestamp:
                log_file_path.unlink()
        except OSError:
            continue
