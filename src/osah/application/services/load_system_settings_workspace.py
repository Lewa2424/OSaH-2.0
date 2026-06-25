from pathlib import Path

from osah.application.services.load_backup_registry import load_backup_registry
from osah.application.services.load_manual_report_settings import load_manual_report_settings
from osah.application.services.load_news_sources import load_news_sources
from osah.domain.services.parse_ui_scale_preset import parse_ui_scale_preset
from osah.application.services.security.load_security_profile import load_security_profile
from osah.domain.entities.settings_workspace import SettingsWorkspace
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.list_app_settings import list_app_settings
from osah.version import __version__


# ###### ЗАВАНТАЖЕННЯ РОБОЧОГО ПРОСТОРУ НАЛАШТУВАНЬ / LOAD SETTINGS WORKSPACE ######
def load_system_settings_workspace(database_path: Path) -> SettingsWorkspace:
    """Builds aggregated settings data for the Settings screen."""

    connection = create_database_connection(database_path)
    try:
        app_settings = list_app_settings(connection)
    finally:
        connection.close()

    backup_snapshots = load_backup_registry(database_path)
    ppe_warning_days = int(app_settings.get("behavior.ppe_warning_days", "7") or "7")
    training_warning_days = int(app_settings.get("behavior.training_warning_days", "7") or "7")
    backup_max_copies = int(app_settings.get("backup.max_copies", "20") or "20")
    backup_auto_enabled = app_settings.get("backup.auto_enabled", "1") == "1"
    news_refresh_time = app_settings.get("news.refresh_time", "09:00") or "09:00"
    ui_scale_preset = parse_ui_scale_preset(app_settings.get("ui.scale_preset"))

    return SettingsWorkspace(
        security_profile=load_security_profile(database_path),
        manual_report_settings=load_manual_report_settings(database_path),
        news_sources=load_news_sources(database_path),
        backup_directory_path=str(database_path.parent / "backups"),
        backup_snapshot_count=len(backup_snapshots),
        backup_max_copies=backup_max_copies,
        backup_auto_enabled=backup_auto_enabled,
        ppe_warning_days=ppe_warning_days,
        training_warning_days=training_warning_days,
        ui_scale_preset=ui_scale_preset,
        news_refresh_time=news_refresh_time,
        app_version=_read_app_version(),
        database_path=str(database_path),
        data_directory_path=str(database_path.parent),
        is_initialized=True,
    )


# ###### ЧИТАННЯ ВЕРСІЇ ПРОЄКТУ / READ PROJECT VERSION ######
def _read_app_version() -> str:
    """Returns the ClearWork version from osah.version."""

    return __version__
