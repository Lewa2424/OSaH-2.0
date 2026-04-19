import tkinter as tk


# ###### ВИДІЛЕННЯ ВИБРАНИХ ТАБЕЛЬНИХ НОМЕРІВ / ВЫДЕЛЕНИЕ ВЫБРАННЫХ ТАБЕЛЬНЫХ НОМЕРОВ ######
def extract_selected_personnel_numbers(listbox: tk.Listbox) -> tuple[str, ...]:
    """Повертає всі вибрані табельні номери з listbox для масового запису.
    Возвращает все выбранные табельные номера из listbox для массовой записи.
    """

    selected_numbers: list[str] = []
    for selected_index in listbox.curselection():
        selected_option = listbox.get(selected_index)
        if " | " not in selected_option:
            continue
        selected_numbers.append(selected_option.split(" | ", maxsplit=1)[0].strip())
    return tuple(selected_numbers)
