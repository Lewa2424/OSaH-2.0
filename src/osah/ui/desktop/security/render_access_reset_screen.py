import customtkinter as ctk
from tkinter import StringVar

from osah.application.services.application_context import ApplicationContext
from osah.application.services.security.build_service_reset_request import build_service_reset_request
from osah.ui.desktop.security.apply_desktop_theme import STYLE_TOKENS
from osah.ui.desktop.security.build_recovery_reset_submit_handler import build_recovery_reset_submit_handler
from osah.ui.desktop.security.build_service_reset_submit_handler import build_service_reset_submit_handler
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


# ###### ВІДОБРАЖЕННЯ ЕКРАНА ВІДНОВЛЕННЯ ДОСТУПУ / ОТРИСОВКА ЭКРАНА ВОССТАНОВЛЕНИЯ ДОСТУПА ######
def render_access_reset_screen(root, application_context: ApplicationContext, on_finished, on_back_to_login) -> None:
    """Показує recovery- і service-reset сценарії без входу до робочого shell.
    Показывает recovery- и service-reset сценарии без входа в рабочий shell.
    """

    clear_desktop_root(root)
    service_reset_request = build_service_reset_request(application_context.database_path)
    recovery_code_var = StringVar()
    service_code_var = StringVar()
    inspector_password_var = StringVar()
    manager_password_var = StringVar()

    container = ctk.CTkFrame(root, fg_color=STYLE_TOKENS["root_background"], corner_radius=0)
    container.pack(fill="both", expand=True, padx=28, pady=28)
    container.grid_columnconfigure(0, weight=5)
    container.grid_columnconfigure(1, weight=6)

    # ---- Ліва інформаційна карточка ----
    info_frame = ctk.CTkFrame(container, **_CARD)
    info_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 14))

    ctk.CTkLabel(
        info_frame,
        text="Аварійне відновлення доступу",
        text_color=STYLE_TOKENS["strong_text"],
        font=("Segoe UI", 16, "bold"),
        anchor="w",
    ).pack(anchor="w", padx=28, pady=(28, 0))

    ctk.CTkLabel(
        info_frame,
        text=(
            "Recovery-код призначений для власника установки. Сервісний код видається окремо під конкретний "
            "ID установки і відкриває тільки режим скидання паролів."
        ),
        text_color=STYLE_TOKENS["muted_text"],
        font=("Segoe UI", 10),
        anchor="w",
        wraplength=420,
        justify="left",
    ).pack(anchor="w", padx=28, pady=(10, 0))

    context_card = ctk.CTkFrame(info_frame, **_INSET)
    context_card.pack(fill="x", padx=28, pady=(20, 0))
    ctk.CTkLabel(
        context_card,
        text="Службові реквізити",
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
        info_frame,
        text="Після успішного скидання система повинна згенерувати новий recovery-код і новий recovery-файл.",
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
        text="Скидання паролів",
        text_color=STYLE_TOKENS["strong_text"],
        font=("Segoe UI", 16, "bold"),
        anchor="w",
    ).grid(row=0, column=0, columnspan=2, sticky="w", padx=28, pady=(28, 0))

    ctk.CTkLabel(
        form_frame,
        text="Вкажіть один із кодів відновлення та задайте нові локальні паролі для ролей інспектора і керівника.",
        text_color=STYLE_TOKENS["muted_text"],
        font=("Segoe UI", 10),
        anchor="w",
        wraplength=520,
        justify="left",
    ).grid(row=1, column=0, columnspan=2, sticky="w", padx=28, pady=(8, 18))

    fields = [
        ("Recovery-код", recovery_code_var, False, 2),
        ("Сервісний код", service_code_var, False, 3),
        ("Новий пароль інспектора", inspector_password_var, True, 4),
        ("Новий пароль керівника", manager_password_var, True, 5),
    ]
    for field_label, var, is_secret, row_idx in fields:
        ctk.CTkLabel(
            form_frame,
            text=field_label,
            text_color=STYLE_TOKENS["muted_text"],
            font=("Segoe UI", 10, "bold"),
            anchor="w",
        ).grid(row=row_idx, column=0, sticky="w", padx=28, pady=(14, 0))
        ctk.CTkEntry(
            form_frame,
            textvariable=var,
            show="*" if is_secret else "",
            **_ENTRY,
        ).grid(row=row_idx, column=1, sticky="ew", padx=(20, 28), pady=(14, 0))

    ctk.CTkButton(
        form_frame,
        text="Скинути через recovery-код",
        command=build_recovery_reset_submit_handler(
            database_path=application_context.database_path,
            recovery_code_var=recovery_code_var,
            inspector_password_var=inspector_password_var,
            manager_password_var=manager_password_var,
            on_reset=on_finished,
        ),
        **_BTN,
    ).grid(row=6, column=0, sticky="w", padx=28, pady=(22, 0))

    ctk.CTkButton(
        form_frame,
        text="Скинути через сервісний код",
        command=build_service_reset_submit_handler(
            database_path=application_context.database_path,
            service_code_var=service_code_var,
            inspector_password_var=inspector_password_var,
            manager_password_var=manager_password_var,
            on_reset=on_finished,
        ),
        **_BTN,
    ).grid(row=6, column=1, sticky="w", padx=(12, 28), pady=(22, 0))

    ctk.CTkButton(
        container,
        text="Повернутися до входу",
        command=on_back_to_login,
        **_BTN_SEC,
    ).grid(row=1, column=1, sticky="w", pady=(14, 0))
