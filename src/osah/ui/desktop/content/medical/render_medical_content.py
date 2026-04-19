from collections.abc import Callable
from pathlib import Path
import customtkinter as ctk

from osah.application.services.load_employee_registry import load_employee_registry
from osah.application.services.load_medical_registry import load_medical_registry
from osah.domain.entities.access_role import AccessRole
from osah.domain.services.security.is_access_role_read_only import is_access_role_read_only
from osah.ui.desktop.content.build_split_workspace import build_split_workspace
from osah.ui.desktop.content.medical.build_medical_screen_refresh_handler import build_medical_screen_refresh_handler
from osah.ui.desktop.content.medical.render_medical_form import render_medical_form
from osah.ui.desktop.content.medical.render_medical_registry_table import render_medical_registry_table
from osah.ui.desktop.content.render_read_only_notice_card import render_read_only_notice_card
from osah.ui.desktop.content.render_screen_header import render_screen_header
from osah.ui.desktop.content.trainings.build_training_employee_options import build_training_employee_options


# ###### ВІДОБРАЖЕННЯ ЕКРАНА МЕДИЦИНИ / ОТРИСОВКА ЭКРАНА МЕДИЦИНЫ ######
def render_medical_content(
    parent: ctk.CTkFrame,
    database_path: Path,
    on_refresh: Callable[[], None],
    access_role: AccessRole = AccessRole.INSPECTOR,
) -> None:
    """Відображає екран модуля медицини з урахуванням ролі доступу.
    Отрисовывает экран модуля медицины с учётом роли доступа.
    """

    for child in parent.winfo_children():
        child.destroy()

    employees = load_employee_registry(database_path)
    medical_records = load_medical_registry(database_path)

    render_screen_header(
        parent,
        "Медицина",
        "Контур меддопуску з мінімально необхідними даними: строки, рішення, обмеження і вплив на можливість роботи.",
    )

    left_frame, right_frame = build_split_workspace(parent)

    if is_access_role_read_only(access_role):
        render_read_only_notice_card(
            left_frame,
            "Режим керівника",
            "Для ролі керівника медичні записи доступні лише для перегляду без змін та доповнень.",
        )
        render_medical_registry_table(right_frame, medical_records)
        return

    employee_options = build_training_employee_options(employees)
    refresh_handler = build_medical_screen_refresh_handler(parent, database_path)
    render_medical_form(left_frame, database_path, employee_options, refresh_handler)
    render_medical_registry_table(right_frame, medical_records)
