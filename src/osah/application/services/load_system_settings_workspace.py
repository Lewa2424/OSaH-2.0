import tomllib
from pathlib import Path

from osah.application.services.load_backup_registry import load_backup_registry
from osah.application.services.load_mail_settings import load_mail_settings
from osah.application.services.load_news_sources import load_news_sources
from osah.application.services.security.load_security_profile import load_security_profile
from osah.domain.entities.settings_workspace import SettingsWorkspace
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.list_app_settings import list_app_settings


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
    training_warning_days = int(app_settings.get("behavior.training_warning_days", "30") or "30")
    backup_max_copies = int(app_settings.get("backup.max_copies", "20") or "20")
    backup_auto_enabled = app_settings.get("backup.auto_enabled", "1") == "1"
    news_refresh_time = app_settings.get("news.refresh_time", "09:00") or "09:00"

    return SettingsWorkspace(
        security_profile=load_security_profile(database_path),
        mail_settings=load_mail_settings(database_path),
        news_sources=load_news_sources(database_path),
        backup_directory_path=str(database_path.parent / "backups"),
        backup_snapshot_count=len(backup_snapshots),
        backup_max_copies=backup_max_copies,
        backup_auto_enabled=backup_auto_enabled,
        ppe_warning_days=ppe_warning_days,
        training_warning_days=training_warning_days,
        news_refresh_time=news_refresh_time,
        app_version=_read_app_version(),
        database_path=str(database_path),
        data_directory_path=str(database_path.parent),
        is_initialized=True,
    )


# ###### ЧИТАННЯ ВЕРСІЇ ПРОЄКТУ / READ PROJECT VERSION ######
def _read_app_version() -> str:
    """Reads application version from pyproject.toml with safe fallback."""

    project_root = Path(__file__).resolve().parents[4]
    pyproject_path = project_root / "pyproject.toml"
    if not pyproject_path.exists():
        return "0.1.0"

    content = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    project_data = content.get("project")
    if isinstance(project_data, dict):
        value = project_data.get("version")
        if isinstance(value, str) and value.strip():
            return value.strip()
    return "0.1.0"
