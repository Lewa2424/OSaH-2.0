from pathlib import Path
from tkinter import StringVar, ttk
import customtkinter as ctk

from osah.domain.entities.backup_snapshot import BackupSnapshot
from osah.ui.desktop.content.settings.build_backup_snapshot_options import build_backup_snapshot_options
from osah.ui.desktop.content.settings.build_create_manual_backup_handler import build_create_manual_backup_handler
from osah.ui.desktop.content.settings.build_restore_backup_handler import build_restore_backup_handler
from osah.ui.desktop.content.ctk_styles import CARD, BTN, BTN_SEC, label_title, label_body


# ###### ВІДОБРАЖЕННЯ ДІЙ РЕЗЕРВУВАННЯ ТА ВІДНОВЛЕННЯ / ОТРИСОВКА ДЕЙСТВИЙ РЕЗЕРВИРОВАНИЯ И ВОССТАНОВЛЕНИЯ ######
def render_backup_actions(
    parent: ctk.CTkFrame,
    database_path: Path,
    backup_snapshots: tuple[BackupSnapshot, ...],
    on_refresh,
) -> None:
    """Відображає керування ручними копіями та відновленням системи.
    Отрисовывает управление ручными копиями и восстановлением системы.
    """

    action_frame = ctk.CTkFrame(parent, **CARD)
    action_frame.pack(fill="x", pady=(0, 20))

    label_title(action_frame, "Резервні копії та відновлення").pack(anchor="w", padx=20, pady=(18, 0))
    label_body(
        action_frame,
        "Автокопія створюється при запуску один раз на добу. Ручна копія доступна в будь-який момент. Перед відновленням завжди формується страховочна копія.",
        wraplength=420,
    ).pack(anchor="w", padx=20, pady=(8, 0))

    button_row = ctk.CTkFrame(action_frame, fg_color="transparent")
    button_row.pack(fill="x", padx=20, pady=(14, 20))

    ctk.CTkButton(
        button_row,
        text="Створити ручну копію",
        command=build_create_manual_backup_handler(database_path, on_refresh),
        **BTN,
    ).pack(fill="x")

    backup_snapshot_options = build_backup_snapshot_options(backup_snapshots)
    selected_backup_var = StringVar(value=backup_snapshot_options[0] if backup_snapshot_options else "")
    
    # Використовуємо ttk.Combobox, оскільки у нас може бути великий список бекапів
    ttk.Combobox(
        button_row,
        values=backup_snapshot_options,
        textvariable=selected_backup_var,
        state="readonly",
    ).pack(fill="x", pady=(10, 0))
    
    ctk.CTkButton(
        button_row,
        text="Відновити обрану копію",
        command=build_restore_backup_handler(database_path, selected_backup_var, on_refresh),
        **BTN_SEC,
    ).pack(fill="x", pady=(10, 0))
