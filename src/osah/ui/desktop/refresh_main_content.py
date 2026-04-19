from tkinter import ttk

from osah.application.services.load_dashboard_snapshot_from_path import load_dashboard_snapshot_from_path
from osah.application.services.load_employee_registry import load_employee_registry
from osah.application.services.load_medical_registry import load_medical_registry
from osah.application.services.load_news_items import load_news_items
from osah.application.services.load_news_sources import load_news_sources
from osah.application.services.load_ppe_registry import load_ppe_registry
from osah.application.services.load_training_registry import load_training_registry
from osah.application.services.load_work_permit_registry import load_work_permit_registry
from osah.domain.entities.app_section import AppSection
from osah.domain.services.security.is_access_role_read_only import is_access_role_read_only
from osah.ui.desktop.content.medical.render_medical_content import render_medical_content
from osah.ui.desktop.content.news.render_news_content import render_news_content
from osah.ui.desktop.content.ppe.render_ppe_content import render_ppe_content
from osah.ui.desktop.content.render_dashboard_content import render_dashboard_content
from osah.ui.desktop.content.render_employee_registry_content import render_employee_registry_content
from osah.ui.desktop.content.render_placeholder_content import render_placeholder_content
from osah.ui.desktop.content.render_read_only_notice_card import render_read_only_notice_card
from osah.ui.desktop.content.reports.render_reports_content import render_reports_content
from osah.ui.desktop.content.settings.render_settings_content import render_settings_content
from osah.ui.desktop.content.trainings.render_trainings_content import render_trainings_content
from osah.ui.desktop.content.work_permits.render_work_permit_content import render_work_permit_content
from osah.ui.desktop.desktop_context import DesktopContext


# ###### ОНОВЛЕННЯ ЦЕНТРАЛЬНОГО КОНТЕНТУ / ОБНОВЛЕНИЕ ЦЕНТРАЛЬНОГО КОНТЕНТА ######
def refresh_main_content(desktop_context: DesktopContext) -> None:
    """Перемальовує центральну область залежно від розділу і ролі доступу.
    Перерисовывает центральную область в зависимости от раздела и роли доступа.
    """

    for child in desktop_context.content_frame.winfo_children():
        child.destroy()

    if desktop_context.selected_section == AppSection.DASHBOARD:
        render_dashboard_content(
            desktop_context.content_frame,
            load_dashboard_snapshot_from_path(desktop_context.application_context.database_path),
        )
        return

    if desktop_context.selected_section == AppSection.EMPLOYEES:
        employees = load_employee_registry(desktop_context.application_context.database_path)
        training_records = load_training_registry(desktop_context.application_context.database_path)
        ppe_records = load_ppe_registry(desktop_context.application_context.database_path)
        medical_records = load_medical_registry(desktop_context.application_context.database_path)
        work_permit_records = load_work_permit_registry(desktop_context.application_context.database_path)
        render_employee_registry_content(
            desktop_context.content_frame,
            employees,
            training_records,
            ppe_records,
            medical_records,
            work_permit_records,
        )
        return

    if desktop_context.selected_section == AppSection.TRAININGS:
        render_trainings_content(
            desktop_context.content_frame,
            desktop_context.application_context.database_path,
            lambda: refresh_main_content(desktop_context),
            access_role=desktop_context.access_role,
        )
        return

    if desktop_context.selected_section == AppSection.PPE:
        render_ppe_content(
            desktop_context.content_frame,
            desktop_context.application_context.database_path,
            lambda: refresh_main_content(desktop_context),
            access_role=desktop_context.access_role,
        )
        return

    if desktop_context.selected_section == AppSection.MEDICAL:
        render_medical_content(
            desktop_context.content_frame,
            desktop_context.application_context.database_path,
            lambda: refresh_main_content(desktop_context),
            access_role=desktop_context.access_role,
        )
        return

    if desktop_context.selected_section == AppSection.WORK_PERMITS:
        render_work_permit_content(
            desktop_context.content_frame,
            desktop_context.application_context.database_path,
            lambda: refresh_main_content(desktop_context),
            access_role=desktop_context.access_role,
        )
        return

    if desktop_context.selected_section == AppSection.SETTINGS:
        if is_access_role_read_only(desktop_context.access_role):
            ttk.Label(desktop_context.content_frame, text="Налаштування", style="ContentTitle.TLabel").pack(
                anchor="w",
                padx=24,
                pady=(24, 8),
            )
            render_read_only_notice_card(
                desktop_context.content_frame,
                "Лише перегляд",
                "Роль керівника не має доступу до імпорту, експорту, резервних копій, відновлення та змін налаштувань.",
            )
            return

        render_settings_content(
            desktop_context.content_frame,
            desktop_context.application_context.database_path,
            lambda: refresh_main_content(desktop_context),
            access_role=desktop_context.access_role,
        )
        return

    if desktop_context.selected_section == AppSection.REPORTS:
        render_reports_content(
            desktop_context.content_frame,
            desktop_context.application_context.database_path,
            lambda: refresh_main_content(desktop_context),
            access_role=desktop_context.access_role,
        )
        return

    if desktop_context.selected_section == AppSection.NEWS_NPA:
        render_news_content(
            desktop_context.content_frame,
            desktop_context.application_context.database_path,
            lambda: refresh_main_content(desktop_context),
            access_role=desktop_context.access_role,
        )
        return

    placeholder_title = ttk.Label(
        desktop_context.content_frame,
        text=desktop_context.selected_section.value,
        style="ContentTitle.TLabel",
    )
    placeholder_title.pack(anchor="w", padx=24, pady=(24, 8))
    render_placeholder_content(desktop_context.content_frame, desktop_context.selected_section)
