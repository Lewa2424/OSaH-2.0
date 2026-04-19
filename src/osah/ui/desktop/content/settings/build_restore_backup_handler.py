from collections.abc import Callable
from pathlib import Path
from tkinter import StringVar, messagebox

from osah.application.services.load_backup_registry import load_backup_registry
from osah.application.services.restore_backup_snapshot import restore_backup_snapshot
from osah.ui.desktop.content.settings.extract_backup_file_name import extract_backup_file_name


# ###### ПОБУДОВА ОБРОБНИКА ВІДНОВЛЕННЯ З РЕЗЕРВНОЇ КОПІЇ / ПОСТРОЕНИЕ ОБРАБОТЧИКА ВОССТАНОВЛЕНИЯ ИЗ РЕЗЕРВНОЙ КОПИИ ######
def build_restore_backup_handler(
    database_path: Path,
    selected_backup_var: StringVar,
    on_success: Callable[[], None],
) -> Callable[[], None]:
    """Повертає обробник відновлення з обраної резервної копії.
    Возвращает обработчик восстановления из выбранной резервной копии.
    """

    # ###### ВІДНОВЛЕННЯ З РЕЗЕРВНОЇ КОПІЇ / ВОССТАНОВЛЕНИЕ ИЗ РЕЗЕРВНОЙ КОПИИ ######
    def restore_selected_backup() -> None:
        """Відновлює базу з вибраної копії після явного підтвердження користувача.
        Восстанавливает базу из выбранной копии после явного подтверждения пользователя.
        """

        selected_backup_file_name = extract_backup_file_name(selected_backup_var)
        if not selected_backup_file_name:
            messagebox.showerror("Помилка відновлення", "Потрібно вибрати резервну копію.")
            return

        if not messagebox.askyesno(
            "Підтвердження відновлення",
            "Перед відновленням буде створено страховочну копію поточного стану. Продовжити?",
        ):
            return

        backup_snapshots = load_backup_registry(database_path)
        backup_snapshot = next(
            (
                candidate_snapshot
                for candidate_snapshot in backup_snapshots
                if candidate_snapshot.file_name == selected_backup_file_name
            ),
            None,
        )
        if backup_snapshot is None:
            messagebox.showerror("Помилка відновлення", "Обрану резервну копію не знайдено.")
            return

        try:
            safety_backup_path = restore_backup_snapshot(database_path, backup_snapshot.file_path)
        except ValueError as error:
            messagebox.showerror("Помилка відновлення", str(error))
            return

        messagebox.showinfo(
            "Відновлення завершено",
            f"Систему відновлено з копії {backup_snapshot.file_name}. Страховочна копія: {safety_backup_path.name}",
        )
        on_success()

    return restore_selected_backup
