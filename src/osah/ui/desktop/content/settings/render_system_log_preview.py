from tkinter import ttk
import customtkinter as ctk

from osah.ui.desktop.content.ctk_styles import CARD, label_title, label_body


# ###### ВІДОБРАЖЕННЯ ПРЕВ'Ю СИСТЕМНОГО ЛОГУ / ОТРИСОВКА ПРЕВЬЮ СИСТЕМНОГО ЛОГА ######
def render_system_log_preview(parent: ctk.CTkFrame, log_lines: tuple[str, ...]) -> None:
    """Відображає останні рядки системного лог-файлу у read-only вигляді.
    Отрисовывает последние строки системного лог-файла в read-only виде.
    """

    card_frame = ctk.CTkFrame(parent, **CARD)
    card_frame.pack(fill="x", pady=(0, 24))

    label_title(card_frame, "Системний лог").pack(anchor="w", padx=20, pady=(18, 0))
    label_body(
        card_frame,
        "Останні технічні події bootstrap, пошти, імпорту, резервування і зовнішніх контурів.",
        wraplength=640,
    ).pack(anchor="w", padx=20, pady=(8, 12))

    if not log_lines:
        label_body(
            card_frame,
            "Файловий системний лог ще не містить подій для перегляду.",
            wraplength=880,
        ).pack(anchor="w", padx=20, pady=(0, 20))
        return

    text_widget = ttk.Treeview(card_frame, columns=("line",), show="headings", height=min(len(log_lines), 8))
    text_widget.heading("line", text="Останні рядки")
    text_widget.column("line", width=880, anchor="w")
    text_widget.pack(fill="x", padx=4, pady=(0, 4))
    
    for log_line in log_lines:
        text_widget.insert("", "end", values=(log_line,))
