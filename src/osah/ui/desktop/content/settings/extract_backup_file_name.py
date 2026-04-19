from tkinter import StringVar


# ###### ВИДІЛЕННЯ ІМЕНІ ФАЙЛУ РЕЗЕРВНОЇ КОПІЇ / ВЫДЕЛЕНИЕ ИМЕНИ ФАЙЛА РЕЗЕРВНОЙ КОПИИ ######
def extract_backup_file_name(selected_backup_var: StringVar) -> str:
    """Повертає ім'я файлу резервної копії з підпису обраного запису.
    Возвращает имя файла резервной копии из подписи выбранной записи.
    """

    selected_option = selected_backup_var.get().strip()
    if " | " not in selected_option:
        return ""
    return selected_option.split(" | ", maxsplit=1)[0].strip()
