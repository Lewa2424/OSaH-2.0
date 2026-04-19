from collections.abc import Callable
from pathlib import Path
from tkinter import messagebox

from osah.application.services.create_backup_snapshot import create_backup_snapshot
from osah.domain.entities.backup_kind import BackupKind


# ###### ПОБУДОВА ОБРОБНИКА РУЧНОЇ РЕЗЕРВНОЇ КОПІЇ / ПОСТРОЕНИЕ ОБРАБОТЧИКА РУЧНОЙ РЕЗЕРВНОЙ КОПИИ ######
def build_create_manual_backup_handler(database_path: Path, on_success: Callable[[], None]) -> Callable[[], None]:
    """Повертає обробник створення ручної резервної копії.
    Возвращает обработчик создания ручной резервной копии.
    """

    # ###### СТВОРЕННЯ РУЧНОЇ РЕЗЕРВНОЇ КОПІЇ / СОЗДАНИЕ РУЧНОЙ РЕЗЕРВНОЙ КОПИИ ######
    def create_manual_backup() -> None:
        """Створює ручну резервну копію локальної системи.
        Создаёт ручную резервную копию локальной системы.
        """

        backup_file_path = create_backup_snapshot(database_path, BackupKind.MANUAL)
        messagebox.showinfo("Резервну копію створено", f"Файл збережено: {backup_file_path}")
        on_success()

    return create_manual_backup
