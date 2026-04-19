from collections.abc import Callable
from pathlib import Path
import customtkinter as ctk

from osah.application.services.load_audit_log_entries import load_audit_log_entries
from osah.application.services.load_backup_registry import load_backup_registry
from osah.application.services.load_latest_employee_import_review import load_latest_employee_import_review
from osah.application.services.load_news_sources import load_news_sources
from osah.application.services.load_recent_system_log_lines import load_recent_system_log_lines
from osah.domain.entities.access_role import AccessRole
from osah.domain.services.security.is_access_role_read_only import is_access_role_read_only
from osah.ui.desktop.content.build_split_workspace import build_split_workspace
from osah.ui.desktop.content.news.render_news_source_table import render_news_source_table
from osah.ui.desktop.content.render_read_only_notice_card import render_read_only_notice_card
from osah.ui.desktop.content.render_screen_header import render_screen_header
from osah.ui.desktop.content.settings.build_settings_screen_refresh_handler import (
    build_settings_screen_refresh_handler,
)
from osah.ui.desktop.content.settings.render_audit_log_table import render_audit_log_table
from osah.ui.desktop.content.settings.render_backup_actions import render_backup_actions
from osah.ui.desktop.content.settings.render_backup_registry_table import render_backup_registry_table
from osah.ui.desktop.content.settings.render_employee_import_drafts_table import render_employee_import_drafts_table
from osah.ui.desktop.content.settings.render_import_batch_summary_card import render_import_batch_summary_card
from osah.ui.desktop.content.settings.render_import_export_actions import render_import_export_actions
from osah.ui.desktop.content.settings.render_news_source_settings_card import render_news_source_settings_card
from osah.ui.desktop.content.settings.render_system_log_preview import render_system_log_preview


# ###### ВІДОБРАЖЕННЯ ЕКРАНА НАЛАШТУВАНЬ / ОТРИСОВКА ЭКРАНА НАСТРОЕК ######
def render_settings_content(
    parent: ctk.CTkFrame,
    database_path: Path,
    on_refresh: Callable[[], None],
    access_role: AccessRole = AccessRole.INSPECTOR,
) -> None:
    """Відображає екран налаштувань, сервісних операцій і журналів.
    Отрисовывает экран настроек, сервисных операций и журналов.
    """

    for child in parent.winfo_children():
        child.destroy()

    import_batch_summary, employee_import_drafts = load_latest_employee_import_review(database_path)
    backup_snapshots = load_backup_registry(database_path)
    news_sources = load_news_sources(database_path)
    audit_log_entries = load_audit_log_entries(database_path, limit=20)
    recent_system_log_lines = load_recent_system_log_lines(database_path, line_limit=20)
    refresh_handler = build_settings_screen_refresh_handler(parent, database_path)

    render_screen_header(
        parent,
        "Налаштування",
        "Службовий контур для імпорту, експорту, резервного копіювання, джерел Новини / НПА, audit-подій і системного журналу.",
    )

    left_frame, right_frame = build_split_workspace(parent, left_weight=5, right_weight=7)

    if is_access_role_read_only(access_role):
        render_read_only_notice_card(
            left_frame,
            "Доступ обмежено",
            "Роль керівника не має права на зміну налаштувань, імпорт, експорт, резервні копії та відновлення.",
        )
        return

    render_import_export_actions(left_frame, database_path, refresh_handler or on_refresh)
    render_backup_actions(left_frame, database_path, backup_snapshots, refresh_handler or on_refresh)
    render_news_source_settings_card(left_frame, database_path, refresh_handler or on_refresh)
    render_import_batch_summary_card(left_frame, import_batch_summary)
    
    render_employee_import_drafts_table(right_frame, employee_import_drafts)
    render_news_source_table(right_frame, news_sources)
    render_audit_log_table(right_frame, audit_log_entries)
    render_system_log_preview(right_frame, recent_system_log_lines)
    render_backup_registry_table(right_frame, backup_snapshots)
