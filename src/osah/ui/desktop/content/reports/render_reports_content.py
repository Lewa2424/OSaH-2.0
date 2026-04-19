from collections.abc import Callable
from pathlib import Path
import customtkinter as ctk

from osah.application.services.build_daily_report_document import build_daily_report_document
from osah.application.services.load_mail_settings import load_mail_settings
from osah.domain.entities.access_role import AccessRole
from osah.domain.services.security.is_access_role_read_only import is_access_role_read_only
from osah.ui.desktop.content.render_read_only_notice_card import render_read_only_notice_card
from osah.ui.desktop.content.render_screen_header import render_screen_header
from osah.ui.desktop.content.reports.build_reports_screen_refresh_handler import build_reports_screen_refresh_handler
from osah.ui.desktop.content.reports.render_daily_report_preview import render_daily_report_preview
from osah.ui.desktop.content.reports.render_mail_settings_form import render_mail_settings_form
from osah.ui.desktop.content.reports.render_report_actions import render_report_actions


# ###### ВІДОБРАЖЕННЯ ЕКРАНА ЗВІТІВ / ОТРИСОВКА ЭКРАНА ОТЧЁТОВ ######
def render_reports_content(
    parent: ctk.CTkFrame,
    database_path: Path,
    on_refresh: Callable[[], None],
    access_role: AccessRole = AccessRole.INSPECTOR,
) -> None:
    """Відображає екран звітів з урахуванням ролі доступу.
    Отрисовывает экран отчётов с учётом роли доступа.
    """
    
    for child in parent.winfo_children():
        child.destroy()

    daily_report_document = build_daily_report_document(database_path)
    mail_settings = load_mail_settings(database_path)
    refresh_handler = build_reports_screen_refresh_handler(parent, database_path)

    render_screen_header(
        parent,
        "Звіти",
        "Щоденний управлінський звіт для керівника, локальна копія та поштова відправка з повторами.",
    )

    if is_access_role_read_only(access_role):
        render_read_only_notice_card(
            parent,
            "Режим керівника",
            "Керівник може переглядати сформований звіт, але не змінює поштові налаштування і не запускає відправлення.",
        )
        render_daily_report_preview(parent, daily_report_document)
        return

    render_report_actions(parent, database_path, refresh_handler or on_refresh)
    render_mail_settings_form(parent, database_path, mail_settings, refresh_handler or on_refresh)
    render_daily_report_preview(parent, daily_report_document)
