from tkinter import Misc


# ###### ПЛАНУВАННЯ КОРОТКОГО CRITICAL-SHAKE / ПЛАНИРОВАНИЕ КОРОТКОГО CRITICAL-SHAKE ######
def schedule_critical_attention_shake(root: Misc) -> None:
    """Виконує коротке кероване тремтіння вікна для критичного сигналу.
    Выполняет короткое управляемое дрожание окна для критического сигнала.
    """

    root.update_idletasks()
    base_x = root.winfo_x()
    base_y = root.winfo_y()
    width = root.winfo_width()
    height = root.winfo_height()
    offsets = (0, -8, 8, -6, 6, -3, 3, 0)

    for step_index, offset in enumerate(offsets):
        root.after(
            step_index * 36,
            lambda current_offset=offset: root.geometry(f"{width}x{height}+{base_x + current_offset}+{base_y}"),
        )
