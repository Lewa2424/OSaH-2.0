import customtkinter as ctk
from tkinter import Misc

from osah.application.services.application_context import ApplicationContext
from osah.application.services.visual.load_visual_alert_state import load_visual_alert_state
from osah.application.services.visual.mark_critical_attention_shake import mark_critical_attention_shake
from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.app_section import AppSection
from osah.ui.desktop.desktop_context import DesktopContext
from osah.ui.desktop.handle_section_selection import handle_section_selection
from osah.ui.desktop.refresh_main_content import refresh_main_content
from osah.ui.desktop.security.apply_desktop_theme import STYLE_TOKENS
from osah.ui.desktop.security.build_available_sections_for_role import build_available_sections_for_role
from osah.ui.desktop.security.clear_desktop_root import clear_desktop_root
from osah.ui.desktop.security.schedule_critical_attention_shake import schedule_critical_attention_shake
from osah.ui.desktop.widgets.build_alert_outline_color import build_alert_outline_color
from osah.ui.desktop.widgets.build_navigation_frame import build_navigation_frame
from osah.ui.desktop.widgets.build_status_bar import build_status_bar
from osah.ui.desktop.widgets.build_top_bar import build_top_bar


# ###### ВІДОБРАЖЕННЯ АВТЕНТИФІКОВАНОГО SHELL / ОТРИСОВКА АУТЕНТИФИЦИРОВАННОГО SHELL ######
def render_authenticated_shell(
    root: Misc,
    application_context: ApplicationContext,
    access_role: AccessRole,
    selected_section: AppSection = AppSection.DASHBOARD,
) -> None:
    """Будує основний desktop-shell після успішної автентифікації.
    Строит основной desktop-shell после успешной аутентификации.
    """

    clear_desktop_root(root)
    visual_alert_state = load_visual_alert_state(application_context.database_path)
    selected_section_level = visual_alert_state.section_levels.get(selected_section)
    selected_outline_color = build_alert_outline_color(selected_section_level) or STYLE_TOKENS["border_color"]

    root.grid_columnconfigure(0, weight=0)
    root.grid_columnconfigure(1, weight=1)
    root.grid_rowconfigure(0, weight=0)
    root.grid_rowconfigure(1, weight=1)
    root.grid_rowconfigure(2, weight=0)

    content_frame = ctk.CTkFrame(
        root,
        fg_color=STYLE_TOKENS["root_background"],
        corner_radius=20,
        border_width=2,
        border_color=selected_outline_color,
    )
    content_frame.grid(row=1, column=1, sticky="nsew", padx=(0, 18), pady=(0, 16))

    desktop_context = DesktopContext(
        root=root,
        content_frame=content_frame,
        application_context=application_context,
        selected_section=selected_section,
        access_role=access_role,
    )

    build_navigation_frame(
        root,
        build_available_sections_for_role(access_role),
        selected_section,
        access_role,
        visual_alert_state.section_levels,
        lambda section: handle_section_selection(desktop_context, section),
    ).grid(row=0, column=0, rowspan=3, sticky="ns", padx=(18, 14), pady=16)
    build_top_bar(root, access_role, selected_section, selected_section_level).grid(
        row=0,
        column=1,
        sticky="ew",
        padx=(0, 18),
        pady=(16, 14),
    )
    build_status_bar(root, application_context.database_path, access_role).grid(
        row=2,
        column=1,
        sticky="ew",
        padx=(0, 18),
        pady=(0, 16),
    )
    refresh_main_content(desktop_context)
    if visual_alert_state.should_shake:
        mark_critical_attention_shake(application_context.database_path)
        schedule_critical_attention_shake(root)
