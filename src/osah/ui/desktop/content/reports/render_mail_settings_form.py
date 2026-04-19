from collections.abc import Callable
from tkinter import BooleanVar, StringVar, ttk
import customtkinter as ctk

from osah.domain.entities.mail_settings import MailSettings
from osah.ui.desktop.content.reports.build_save_mail_settings_handler import build_save_mail_settings_handler
from osah.ui.desktop.content.ctk_styles import CARD, BTN, ENTRY, CHECKBOX, label_title, label_muted


# ###### ВІДОБРАЖЕННЯ ФОРМИ ПОШТОВИХ НАЛАШТУВАНЬ / ОТРИСОВКА ФОРМЫ ПОЧТОВЫХ НАСТРОЕК ######
def render_mail_settings_form(parent: ctk.CTkFrame, database_path, mail_settings: MailSettings, on_success: Callable[[], None]) -> None:
    """Відображає форму SMTP-настроек та параметрів щоденного звіту.
    Отрисовывает форму SMTP-настроек и параметров ежедневного отчёта.
    """

    form_frame = ctk.CTkFrame(parent, **CARD)
    form_frame.pack(fill="x", pady=(0, 20))

    label_title(form_frame, "Поштові налаштування").grid(row=0, column=0, columnspan=2, sticky="w", padx=20, pady=(20, 0))

    daily_report_enabled_var = BooleanVar(value=mail_settings.daily_report_enabled)
    smtp_host_var = StringVar(value=mail_settings.smtp_host)
    smtp_port_var = StringVar(value=str(mail_settings.smtp_port))
    smtp_username_var = StringVar(value=mail_settings.smtp_username)
    smtp_password_var = StringVar(value=mail_settings.smtp_password)
    sender_email_var = StringVar(value=mail_settings.sender_email)
    recipient_email_var = StringVar(value=mail_settings.recipient_email)
    use_tls_var = BooleanVar(value=mail_settings.use_tls)

    ctk.CTkCheckBox(
        form_frame,
        text="Увімкнути щоденний звіт",
        variable=daily_report_enabled_var,
        **CHECKBOX
    ).grid(row=1, column=0, columnspan=2, sticky="w", padx=20, pady=(16, 0))

    field_specs = (
        ("SMTP host", 2),
        ("SMTP port", 3),
        ("SMTP username", 4),
        ("SMTP password", 5),
        ("Від кого", 6),
        ("Кому", 7),
    )
    
    for field_label, row_index in field_specs:
        label_muted(form_frame, field_label).grid(row=row_index, column=0, sticky="w", padx=20, pady=(16, 0))

    ctk.CTkEntry(form_frame, textvariable=smtp_host_var, **ENTRY).grid(row=2, column=1, sticky="ew", padx=(10, 20), pady=(16, 0))
    ctk.CTkEntry(form_frame, textvariable=smtp_port_var, **ENTRY).grid(row=3, column=1, sticky="ew", padx=(10, 20), pady=(16, 0))
    ctk.CTkEntry(form_frame, textvariable=smtp_username_var, **ENTRY).grid(row=4, column=1, sticky="ew", padx=(10, 20), pady=(16, 0))
    ctk.CTkEntry(form_frame, textvariable=smtp_password_var, show="*", **ENTRY).grid(row=5, column=1, sticky="ew", padx=(10, 20), pady=(16, 0))
    ctk.CTkEntry(form_frame, textvariable=sender_email_var, **ENTRY).grid(row=6, column=1, sticky="ew", padx=(10, 20), pady=(16, 0))
    ctk.CTkEntry(form_frame, textvariable=recipient_email_var, **ENTRY).grid(row=7, column=1, sticky="ew", padx=(10, 20), pady=(16, 0))

    ctk.CTkCheckBox(
        form_frame,
        text="Використовувати STARTTLS",
        variable=use_tls_var,
        **CHECKBOX
    ).grid(row=8, column=0, columnspan=2, sticky="w", padx=20, pady=(16, 0))

    form_frame.grid_columnconfigure(1, weight=1)
    
    ctk.CTkButton(
        form_frame,
        text="Зберегти поштові налаштування",
        command=build_save_mail_settings_handler(
            database_path=database_path,
            daily_report_enabled_var=daily_report_enabled_var,
            smtp_host_var=smtp_host_var,
            smtp_port_var=smtp_port_var,
            smtp_username_var=smtp_username_var,
            smtp_password_var=smtp_password_var,
            sender_email_var=sender_email_var,
            recipient_email_var=recipient_email_var,
            use_tls_var=use_tls_var,
            last_sent_date=mail_settings.last_sent_date,
            on_success=on_success,
        ),
        **BTN,
    ).grid(row=9, column=0, columnspan=2, sticky="w", padx=20, pady=(24, 20))
