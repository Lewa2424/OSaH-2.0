import customtkinter as ctk

from osah.ui.desktop.content.ctk_styles import label_content_title, label_body


# ###### ВІДОБРАЖЕННЯ ЗАГОЛОВКА ЕКРАНА / ОТРИСОВКА ЗАГОЛОВКА ЭКРАНА ######
def render_screen_header(parent, title_text: str, description_text: str) -> None:
    """Відображає стандартизований заголовок екрану з коротким операційним описом.
    Отрисовывает стандартизированный заголовок экрана с кратким операционным описанием.
    """

    label_content_title(parent, title_text).pack(anchor="w", padx=24, pady=(24, 8))
    label_body(parent, description_text, wraplength=980).pack(anchor="w", padx=24, pady=(0, 16))
