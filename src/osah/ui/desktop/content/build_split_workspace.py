import customtkinter as ctk


# ###### ПОБУДОВА РОБОЧОГО SPLIT-LAYOUT / ПОСТРОЕНИЕ РАБОЧЕГО SPLIT-LAYOUT ######
def build_split_workspace(
    parent: ctk.CTkFrame,
    left_weight: int = 5,
    right_weight: int = 7,
) -> tuple[ctk.CTkFrame, ctk.CTkFrame]:
    """Створює двоколонковий робочий layout для форм і реєстрів.
    Создаёт двухколоночный рабочий layout для форм и реестров.
    """

    workspace_frame = ctk.CTkFrame(parent, fg_color="transparent", corner_radius=0)
    workspace_frame.pack(fill="both", expand=True, padx=24, pady=(0, 24))
    workspace_frame.grid_columnconfigure(0, weight=left_weight)
    workspace_frame.grid_columnconfigure(1, weight=right_weight)
    workspace_frame.grid_rowconfigure(0, weight=1)

    left_frame = ctk.CTkScrollableFrame(workspace_frame, fg_color="transparent", corner_radius=0)
    left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

    right_frame = ctk.CTkFrame(workspace_frame, fg_color="transparent", corner_radius=0)
    right_frame.grid(row=0, column=1, sticky="nsew")

    return left_frame, right_frame
