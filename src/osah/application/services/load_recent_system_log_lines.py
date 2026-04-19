from pathlib import Path

from osah.infrastructure.logging.build_log_file_path_from_database_path import build_log_file_path_from_database_path


# ###### ЗАВАНТАЖЕННЯ ОСТАННІХ РЯДКІВ СИСТЕМНОГО ЛОГУ / ЗАГРУЗКА ПОСЛЕДНИХ СТРОК СИСТЕМНОГО ЛОГА ######
def load_recent_system_log_lines(database_path: Path, line_limit: int = 20) -> tuple[str, ...]:
    """Повертає останні рядки системного лог-файлу для службового перегляду.
    Возвращает последние строки системного лог-файла для служебного просмотра.
    """

    log_file_path = build_log_file_path_from_database_path(database_path)
    if not log_file_path.exists():
        return ()

    log_lines = log_file_path.read_text(encoding="utf-8").splitlines()
    return tuple(log_lines[-line_limit:])
