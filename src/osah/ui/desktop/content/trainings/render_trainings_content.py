from collections.abc import Callable
from pathlib import Path
import customtkinter as ctk

from osah.application.services.load_employee_registry import load_employee_registry
from osah.application.services.load_training_registry import load_training_registry
from osah.application.services.load_training_registry_rows import load_training_registry_rows
from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.training_registry_filter import TrainingRegistryFilter
from osah.domain.services.security.is_access_role_read_only import is_access_role_read_only
from osah.ui.desktop.content.build_paned_workspace import build_paned_workspace
from osah.ui.desktop.content.render_read_only_notice_card import render_read_only_notice_card
from osah.ui.desktop.content.render_screen_header import render_screen_header
from osah.ui.desktop.content.trainings.build_training_employee_options import build_training_employee_options
from osah.ui.desktop.content.trainings.build_trainings_screen_refresh_handler import build_trainings_screen_refresh_handler
from osah.ui.desktop.content.trainings.render_training_batch_form import render_training_batch_form
from osah.ui.desktop.content.trainings.render_training_edit_form import render_training_edit_form
from osah.ui.desktop.content.trainings.render_training_filter_bar import render_training_filter_bar
from osah.ui.desktop.content.trainings.render_training_form import render_training_form
from osah.ui.desktop.content.trainings.render_training_registry_table import render_training_registry_table


# ###### ВІДОБРАЖЕННЯ ЕКРАНА ІНСТРУКТАЖІВ / ОТРИСОВКА ЭКРАНА ИНСТРУКТАЖЕЙ ######
def render_trainings_content(
    parent: ctk.CTkFrame,
    database_path: Path,
    on_refresh: Callable[[], None],
    selected_filter: TrainingRegistryFilter = TrainingRegistryFilter.ALL,
    access_role: AccessRole = AccessRole.INSPECTOR,
) -> None:
    """Відображає екран модуля інструктажів з урахуванням ролі доступу.
    Отрисовывает экран модуля инструктажей с учётом роли доступа.
    """

    for child in parent.winfo_children():
        child.destroy()

    employees = load_employee_registry(database_path)
    training_records = load_training_registry(database_path)
    registry_rows = load_training_registry_rows(database_path, selected_filter)

    render_screen_header(
        parent,
        "Інструктажі",
        "Єдиний контур для створення, масового внесення, редагування та контролю строків інструктажів.",
    )

    left_frame, right_frame = build_paned_workspace(parent)
    render_training_filter_bar(left_frame, database_path, on_refresh, selected_filter, access_role)
    
    if is_access_role_read_only(access_role):
        render_read_only_notice_card(
            left_frame,
            "Режим керівника",
            "Для ролі керівника інструктажі доступні лише для перегляду без створення, редагування та видалення записів.",
        )
        render_training_registry_table(right_frame, registry_rows)
        return

    employee_options = build_training_employee_options(employees)
    refresh_handler = build_trainings_screen_refresh_handler(parent, database_path, selected_filter, access_role)
    render_training_form(left_frame, database_path, employee_options, refresh_handler)
    render_training_batch_form(left_frame, database_path, employee_options, refresh_handler)
    render_training_edit_form(left_frame, database_path, employee_options, training_records, refresh_handler)
    render_training_registry_table(right_frame, registry_rows)
