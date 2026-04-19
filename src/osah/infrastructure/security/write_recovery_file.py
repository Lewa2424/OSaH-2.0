from pathlib import Path


# ###### ЗАПИС RECOVERY-ФАЙЛУ / ЗАПИСЬ RECOVERY-ФАЙЛА ######
def write_recovery_file(file_path: Path, file_content: str) -> None:
    """Створює або оновлює recovery-файл на локальному диску.
    Создаёт или обновляет recovery-файл на локальном диске.
    """

    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(file_content, encoding="utf-8")
