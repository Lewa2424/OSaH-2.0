import customtkinter as ctk
from tkinter import StringVar

from osah.application.services.application_context import ApplicationContext
from osah.application.services.security.build_service_reset_request import build_service_reset_request
from osah.domain.entities.access_role import AccessRole
from osah.ui.desktop.security.apply_desktop_theme import STYLE_TOKENS
from osah.ui.desktop.security.build_login_submit_handler import build_login_submit_handler
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
_BTN_SEC = {
    "corner_radius": 15,
    "fg_color": STYLE_TOKENS["surface_background"],
    "hover_color": "#F3F4F6",
    "text_color": STYLE_TOKENS["strong_text"],
    "border_width": 1,
    "border_color": STYLE_TOKENS["border_color"],
    "font": ("Segoe UI", 11),
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


# ###### ВІДОБРАЖЕННЯ ЕКРАНА ВХОДУ / ОТРИСОВКА ЭКРАНА ВХОДА ######
def render_login_screen(root, application_context: ApplicationContext, on_authenticated, on_recovery_requested) -> None:
    """Показує екран входу з ролями доступу і службовими даними установки.
    Показывает экран входа с ролями доступа и служебными данными установки.
    """

    clear_desktop_root(root)
    service_reset_request = build_service_reset_request(application_context.database_path)
    access_role_var = StringVar(value=AccessRole.INSPECTOR.value)
    password_var = StringVar()

    container = ctk.CTkFrame(root, fg_color=STYLE_TOKENS["root_background"], corner_radius=0)
    container.pack(fill="both", expand=True, padx=28, pady=28)
    container.grid_columnconfigure(0, weight=5)
    container.grid_columnconfigure(1, weight=6)
    container.grid_rowconfigure(0, weight=1)

    # ---- Ліва інформаційна карточка ----
    hero_frame = ctk.CTkFrame(container, **_CARD)
    hero_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 14))

    ctk.CTkLabel(
        hero_frame,
        text="Вхід до локального контуру",
        text_color=STYLE_TOKENS["strong_text"],
        font=("Segoe UI", 16, "bold"),
        anchor="w",
    ).pack(anchor="w", padx=28, pady=(28, 0))

    ctk.CTkLabel(
        hero_frame,
        text=(
            "Робочий shell відкривається тільки після локальної автентифікації. "
            "Інспектор отримує повний доступ, керівник працює у режимі перегляду."
        ),
        text_color=STYLE_TOKENS["muted_text"],
        font=("Segoe UI", 10),
        anchor="w",
        wraplength=420,
        justify="left",
    ).pack(anchor="w", padx=28, pady=(10, 0))

    context_card = ctk.CTkFrame(hero_frame, **_INSET)
    context_card.pack(fill="x", padx=28, pady=(20, 0))
    ctk.CTkLabel(
        context_card,
        text="Локальна установка",
        text_color=STYLE_TOKENS["muted_text"],
        font=("Segoe UI", 10, "bold"),
        anchor="w",
    ).pack(anchor="w", padx=16, pady=(16, 0))
    ctk.CTkLabel(
        context_card,
        text=(
            f"ID установки: {service_reset_request.installation_id}\n"
            f"Номер сервісного запиту: {service_reset_request.request_counter}"
        ),
        text_color=STYLE_TOKENS["strong_text"],
        font=("Segoe UI", 10),
        anchor="w",
        justify="left",
    ).pack(anchor="w", padx=16, pady=(8, 16))

    ctk.CTkLabel(
        hero_frame,
        text="Доступ і recovery-механіка працюють локально, без окремого сервера і без універсального майстер-пароля.",
        text_color=STYLE_TOKENS["muted_text"],
        font=("Segoe UI", 10, "bold"),
        anchor="w",
        wraplength=420,
        justify="left",
    ).pack(anchor="w", padx=28, pady=(20, 28))

    # ---- Права форма входу ----
    login_frame = ctk.CTkFrame(container, **_CARD)
    login_frame.grid(row=0, column=1, sticky="nsew")
    login_frame.grid_columnconfigure(1, weight=1)

    ctk.CTkLabel(
        login_frame,
        text="Авторизація",
        text_color=STYLE_TOKENS["strong_text"],
        font=("Segoe UI", 16, "bold"),
        anchor="w",
    ).grid(row=0, column=0, columnspan=3, sticky="w", padx=28, pady=(28, 0))

    ctk.CTkLabel(
        login_frame,
        text="Оберіть роль і введіть пароль програми для входу в робочий контур.",
        text_color=STYLE_TOKENS["muted_text"],
        font=("Segoe UI", 10),
        anchor="w",
        wraplength=520,
        justify="left",
    ).grid(row=1, column=0, columnspan=3, sticky="w", padx=28, pady=(8, 18))

    ctk.CTkLabel(
        login_frame,
        text="Роль доступу",
        text_color=STYLE_TOKENS["muted_text"],
        font=("Segoe UI", 10, "bold"),
        anchor="w",
    ).grid(row=2, column=0, sticky="w", padx=28)

    ctk.CTkRadioButton(
        login_frame,
        text="Інспектор",
        value=AccessRole.INSPECTOR.value,
        variable=access_role_var,
        font=("Segoe UI", 11),
        text_color=STYLE_TOKENS["strong_text"],
        fg_color=STYLE_TOKENS["accent_background"],
        hover_color=STYLE_TOKENS["accent_hover_background"],
    ).grid(row=2, column=1, sticky="w", padx=(18, 0))

    ctk.CTkRadioButton(
        login_frame,
        text="Керівник",
        value=AccessRole.MANAGER.value,
        variable=access_role_var,
        font=("Segoe UI", 11),
        text_color=STYLE_TOKENS["strong_text"],
        fg_color=STYLE_TOKENS["accent_background"],
        hover_color=STYLE_TOKENS["accent_hover_background"],
    ).grid(row=2, column=2, sticky="w", padx=(12, 28))

    ctk.CTkLabel(
        login_frame,
        text="Пароль",
        text_color=STYLE_TOKENS["muted_text"],
        font=("Segoe UI", 10, "bold"),
        anchor="w",
    ).grid(row=3, column=0, sticky="w", padx=28, pady=(16, 0))

    ctk.CTkEntry(
        login_frame,
        textvariable=password_var,
        show="*",
        **_ENTRY,
    ).grid(row=3, column=1, columnspan=2, sticky="ew", padx=(18, 28), pady=(16, 0))

    ctk.CTkButton(
        login_frame,
        text="Увійти",
        command=build_login_submit_handler(
            database_path=application_context.database_path,
            access_role_var=access_role_var,
            password_var=password_var,
            on_authenticated=on_authenticated,
        ),
        **_BTN,
    ).grid(row=4, column=0, sticky="w", padx=28, pady=(22, 28))

    ctk.CTkButton(
        login_frame,
        text="Відновити доступ",
        command=on_recovery_requested,
        **_BTN_SEC,
    ).grid(row=4, column=1, sticky="w", padx=(12, 0), pady=(22, 28))
