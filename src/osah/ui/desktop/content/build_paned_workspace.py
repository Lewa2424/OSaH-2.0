import customtkinter as ctk
from tkinter import PanedWindow, HORIZONTAL, Frame as TkFrame

from osah.ui.desktop.security.apply_desktop_theme import STYLE_TOKENS


# ###### ПОБУДОВА РОБОЧОГО PANED-LAYOUT / ПОСТРОЕНИЕ РАБОЧЕГО PANED-LAYOUT ######
def build_paned_workspace(
    parent: ctk.CTkFrame,
) -> tuple[ctk.CTkScrollableFrame, ctk.CTkFrame]:
    """Створює двоколонковий робочий layout з рухомим розділювачем.
    Создает двухколоночный рабочий layout с подвижным разделителем.
    """

    workspace_frame = ctk.CTkFrame(parent, fg_color="transparent", corner_radius=0)
    workspace_frame.pack(fill="both", expand=True, padx=24, pady=(0, 24))

    # PanedWindow — нативний tk-компонент. Його фон — синя лінія-розділювач.
    paned = PanedWindow(
        workspace_frame,
        orient=HORIZONTAL,
        bg=STYLE_TOKENS["accent_background"],
        bd=0,
        sashwidth=4,
        sashcursor="sb_h_double_arrow",
        sashrelief="flat",
    )
    paned.pack(fill="both", expand=True)

    # Використовуємо НАТИВНІ tk.Frame як дочірні для PanedWindow.
    # Це ключова відмінність від CTkFrame: tk.Frame має явний bg і є повністю
    # непрозорим на рівні ОС — синій фон PanedWindow не просвічується крізь нього.
    root_bg = STYLE_TOKENS["root_background"]

    left_wrapper = TkFrame(paned, bg=root_bg)
    left_frame = ctk.CTkScrollableFrame(left_wrapper, fg_color="transparent", corner_radius=0)
    left_frame.pack(fill="both", expand=True)

    right_wrapper = TkFrame(paned, bg=root_bg)
    right_frame = ctk.CTkFrame(right_wrapper, fg_color="transparent", corner_radius=0)
    right_frame.pack(fill="both", expand=True)

    paned.add(left_wrapper, minsize=350, stretch="always")
    paned.add(right_wrapper, minsize=400, stretch="always")

    return left_frame, right_frame
