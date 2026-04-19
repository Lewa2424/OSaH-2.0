from tkinter import Misc


# ###### ОЧИЩЕННЯ КОРЕНЕВОГО ВІКНА / ОЧИСТКА КОРНЕВОГО ОКНА ######
def clear_desktop_root(root: Misc) -> None:
    """Видаляє поточний вміст кореневого вікна перед перемальовуванням.
    Удаляет текущее содержимое корневого окна перед перерисовкой.
    """

    for child in root.winfo_children():
        child.destroy()
