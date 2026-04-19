from collections.abc import Callable
from pathlib import Path
import customtkinter as ctk

from osah.application.services.load_employee_registry import load_employee_registry
from osah.application.services.load_work_permit_registry import load_work_permit_registry
from osah.domain.entities.access_role import AccessRole
from osah.domain.services.security.is_access_role_read_only import is_access_role_read_only
from osah.ui.desktop.content.build_split_workspace import build_split_workspace
from osah.ui.desktop.content.render_read_only_notice_card import render_read_only_notice_card
from osah.ui.desktop.content.render_screen_header import render_screen_header
from osah.ui.desktop.content.trainings.build_training_employee_options import build_training_employee_options
from osah.ui.desktop.content.work_permits.build_work_permit_screen_refresh_handler import (
    build_work_permit_screen_refresh_handler,
)
from osah.ui.desktop.content.work_permits.render_work_permit_close_form import render_work_permit_close_form
from osah.ui.desktop.content.work_permits.render_work_permit_form import render_work_permit_form
from osah.ui.desktop.content.work_permits.render_work_permit_registry_table import render_work_permit_registry_table


# ###### ВІДОБРАЖЕННЯ ЕКРАНА НАРЯДІВ / ОТРИСОВКА ЭКРАНА НАРЯДОВ ######
def render_work_permit_content(
    parent: ctk.CTkFrame,
    database_path: Path,
    on_refresh: Callable[[], None],
    access_role: AccessRole = AccessRole.INSPECTOR,
) -> None:
    """Відображає екран модуля нарядів-допусків з урахуванням ролі доступу.
    Отрисовывает экран модуля нарядов-допусков с учётом роли доступа.
    """

    for child in parent.winfo_children():
        child.destroy()

    employees = load_employee_registry(database_path)
    work_permit_records = load_work_permit_registry(database_path)

    render_screen_header(
        parent,
        "Наряди-допуски",
        "Контроль робіт підвищеної небезпеки: відкриття нарядів, визначення ролей учасників і ручне закриття.",
    )

    left_frame, right_frame = build_split_workspace(parent, left_weight=4, right_weight=8)

    if is_access_role_read_only(access_role):
        render_read_only_notice_card(
            left_frame,
            "Режим керівника",
            "Для ролі керівника наряди-допуски доступні лише для перегляду без можливості відкриття чи закриття.",
        )
        render_work_permit_registry_table(right_frame, work_permit_records)
        return

    employee_options = build_training_employee_options(employees)
    refresh_handler = build_work_permit_screen_refresh_handler(parent, database_path)
    render_work_permit_form(left_frame, database_path, employee_options, refresh_handler)
    render_work_permit_close_form(left_frame, database_path, work_permit_records, refresh_handler)
    render_work_permit_registry_table(right_frame, work_permit_records)
