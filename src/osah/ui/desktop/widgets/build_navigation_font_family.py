import tkinter as tk
from tkinter import font as tk_font


# ###### ВИБІР ШРИФТУ НАВІГАЦІЇ / ВЫБОР ШРИФТА НАВИГАЦИИ ######
def build_navigation_font_family(widget: tk.Misc) -> str:
    """Повертає найкращий доступний геометричний гротеск для sidebar-навігації.
    Возвращает лучший доступный геометрический гротеск для sidebar-навигации.
    """

    available_families = {family.casefold() for family in tk_font.families(widget)}
    for candidate in ("Proxima Nova", "Montserrat", "Inter", "Candara", "Segoe UI"):
        if candidate.casefold() in available_families:
            return candidate
    return "Segoe UI"
