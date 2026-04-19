import customtkinter as ctk
from tkinter import StringVar

from osah.application.services.application_context import ApplicationContext
from osah.application.services.security.load_security_profile import load_security_profile
from osah.ui.desktop.security.apply_desktop_theme import STYLE_TOKENS
from osah.ui.desktop.security.build_initial_security_setup_submit_handler import (
    build_initial_security_setup_submit_handler,
)
from osah.ui.desktop.security.clear_desktop_root import clear_desktop_root

_CARD = {
    "fg_color": STYLE_TOKENS["surface_background"],
    "corner_radius": 20,
    "border_width": 1,
    "border_color": STYLE_TOKENS["border_color"],
}
_BTN = {
    "corner_radius": 15,
    "fg_color": STYLE_TOKENS["accent_background"],
    "hover_color": STYLE_TOKENS["accent_hover_background"],
    "text_color": "#FFFFFF",
    "border_width": 1,
    "border_color": STYLE_TOKENS["accent_hover_background"],
    "font": ("Segoe UI", 11, "bold"),
    "height": 40,
}
_ENTRY = {
    "corner_radius": 12,
    "border_color": STYLE_TOKENS["border_color"],
    "fg_color": STYLE_TOKENS["surface_background"],
    "text_color": STYLE_TOKENS["strong_text"],
    "font": ("Segoe UI", 11),
    "height": 38,
}
_INSET = {
    "fg_color": STYLE_TOKENS["shell_surface"],
    "corner_radius": 12,
    "border_width": 1,
    "border_color": STYLE_TOKENS["border_color"],
}


# ###### ВІДОБРАЖЕННЯ ЕКРАНА ПЕРВИННОГО НАЛАШТУВАННЯ / ОТРИСОВКА ЭКРАНА ПЕРВИЧНОЙ НАСТРОЙКИ ######
def render_initial_security_setup_screen(root, application_context: ApplicationContext, on_configured) -> None:
    """Показує перший екран налаштування паролів і recovery-механіки.
    Показывает первый экран настройки паролей и recovery-механики.
    """

    clear_desktop_root(root)
    security_profile = load_security_profile(application_context.database_path)
    inspector_password_var = StringVar()
    manager_password_var = StringVar()

    container = ctk.CTkFrame(root, fg_color=STYLE_TOKENS["root_background"], corner_radius=0)
    container.pack(fill="both", expand=True, padx=28, pady=28)
    container.grid_columnconfigure(0, weight=5)
    container.grid_columnconfigure(1, weight=6)

    # ---- Ліва інформаційна карточка ----
    intro_frame = ctk.CTkFrame(container, **_CARD)
    intro_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 14))

    ctk.CTkLabel(
        intro_frame,
        text="Первинне налаштування доступу",
        text_color=STYLE_TOKENS["strong_text"],
        font=("Segoe UI", 16, "bold"),
        anchor="w",
    ).pack(anchor="w", padx=28, pady=(28, 0))

    ctk.CTkLabel(
        intro_frame,
        text=(
            "На першому запуску потрібно зафіксувати окремі паролі для інспектора і керівника. "
            "Після збереження система створить recovery-файл і ввімкне локальний security-контур."
        ),
        text_color=STYLE_TOKENS["muted_text"],
        font=("Segoe UI", 10),
        anchor="w",
        wraplength=420,
        justify="left",
    ).pack(anchor="w", padx=28, pady=(10, 0))

    info_card = ctk.CTkFrame(intro_frame, **_INSET)
    info_card.pack(fill="x", padx=28, pady=(20, 0))
    ctk.CTkLabel(
        info_card,
        text="ID установки",
        text_color=STYLE_TOKENS["muted_text"],
        font=("Segoe UI", 10, "bold"),
        anchor="w",
    ).pack(anchor="w", padx=16, pady=(16, 0))
    ctk.CTkLabel(
        info_card,
        text=security_profile.installation_id,
        text_color=STYLE_TOKENS["strong_text"],
        font=("Segoe UI", 14, "bold"),
        anchor="w",
    ).pack(anchor="w", padx=16, pady=(8, 16))

    ctk.CTkLabel(
        intro_frame,
        text="Паролі не зберігаються у відкритому вигляді, а recovery-файл потрібно тримати окремо від робочого ПК.",
        text_color=STYLE_TOKENS["muted_text"],
        font=("Segoe UI", 10, "bold"),
        anchor="w",
        wraplength=420,
        justify="left",
    ).pack(anchor="w", padx=28, pady=(20, 28))

    # ---- Права форма ----
    form_frame = ctk.CTkFrame(container, **_CARD)
    form_frame.grid(row=0, column=1, sticky="nsew")
    form_frame.grid_columnconfigure(1, weight=1)

    ctk.CTkLabel(
        form_frame,
        text="Параметри першого запуску",
        text_color=STYLE_TOKENS["strong_text"],
        font=("Segoe UI", 16, "bold"),
        anchor="w",
    ).grid(row=0, column=0, columnspan=2, sticky="w", padx=28, pady=(28, 0))

    ctk.CTkLabel(
        form_frame,
        text="Задайте окремі локальні паролі для повного та read-only доступу.",
        text_color=STYLE_TOKENS["muted_text"],
        font=("Segoe UI", 10),
        anchor="w",
        wraplength=520,
        justify="left",
    ).grid(row=1, column=0, columnspan=2, sticky="w", padx=28, pady=(8, 18))

    ctk.CTkLabel(
        form_frame,
        text="Пароль інспектора",
        text_color=STYLE_TOKENS["muted_text"],
        font=("Segoe UI", 10, "bold"),
        anchor="w",
    ).grid(row=2, column=0, sticky="w", padx=28)

    ctk.CTkEntry(form_frame, textvariable=inspector_password_var, show="*", **_ENTRY).grid(
        row=2, column=1, sticky="ew", padx=(20, 28)
    )

    ctk.CTkLabel(
        form_frame,
        text="Пароль керівника",
        text_color=STYLE_TOKENS["muted_text"],
        font=("Segoe UI", 10, "bold"),
        anchor="w",
    ).grid(row=3, column=0, sticky="w", padx=28, pady=(14, 0))

    ctk.CTkEntry(form_frame, textvariable=manager_password_var, show="*", **_ENTRY).grid(
        row=3, column=1, sticky="ew", padx=(20, 28), pady=(14, 0)
    )

    ctk.CTkButton(
        form_frame,
        text="Завершити налаштування",
        command=build_initial_security_setup_submit_handler(
            database_path=application_context.database_path,
            inspector_password_var=inspector_password_var,
            manager_password_var=manager_password_var,
            on_configured=on_configured,
        ),
        **_BTN,
    ).grid(row=4, column=0, columnspan=2, sticky="w", padx=28, pady=(22, 28))
