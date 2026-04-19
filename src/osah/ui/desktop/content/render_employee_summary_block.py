import customtkinter as ctk

from osah.ui.desktop.content.ctk_styles import INSET, label_title, label_body


# ###### ВІДОБРАЖЕННЯ БЛОКУ ПІДСУМКУ / ОТРИСОВКА БЛОКА СВОДКИ ######
def render_employee_summary_block(parent, title_text: str, summary_lines: tuple[str, ...]) -> None:
    """Відображає окремий тематичний блок короткої сводки в картці працівника.
    Отрисовывает отдельный тематический блок краткой сводки в карточке сотрудника.
    """

    block_frame = ctk.CTkFrame(parent, **INSET)
    block_frame.pack(fill="x", pady=(14, 0))

    label_title(block_frame, title_text).pack(anchor="w", padx=16, pady=(14, 0))
    for summary_line in summary_lines:
        label_body(block_frame, summary_line, wraplength=360).pack(anchor="w", padx=16, pady=(8, 0))
    ctk.CTkFrame(block_frame, fg_color="transparent", height=14).pack()
