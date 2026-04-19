import customtkinter as ctk


# ###### СТВОРЕННЯ ОСНОВНОГО ВІКНА / СОЗДАНИЕ ОСНОВНОГО ОКНА ######
def create_root_window() -> ctk.CTk:
    """Створює кореневе вікно desktop-застосунку з glassmorphism-темою на світлому фоні.
    Создаёт корневое окно desktop-приложения с glassmorphism-темой на светлом фоне.
    """

    ctk.set_appearance_mode("Light")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("OSaH 2.0")
    root.geometry("1400x860")
    root.minsize(1220, 760)
    root.configure(fg_color="#F0F2F5")
    return root
