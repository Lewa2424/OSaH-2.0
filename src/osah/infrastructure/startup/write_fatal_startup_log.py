import traceback
from pathlib import Path


# ###### ЗАПИС ФАТАЛЬНОЇ ПОМИЛКИ ЗАПУСКУ / WRITE FATAL STARTUP ERROR LOG ######
def write_fatal_startup_log(log_file_path: Path, error: BaseException) -> None:
    """Записує traceback фатальної помилки у файл логу.
    Writes a fatal startup error traceback into the log file.
    """

    log_file_path.parent.mkdir(parents=True, exist_ok=True)
    error_text = "".join(traceback.format_exception(type(error), error, error.__traceback__))
    with log_file_path.open("a", encoding="utf-8") as log_file:
        log_file.write("\n--- FATAL STARTUP ERROR ---\n")
        log_file.write(error_text)
