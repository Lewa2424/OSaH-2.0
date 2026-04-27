from dataclasses import dataclass

from osah.domain.entities.mail_settings import MailSettings
from osah.domain.entities.news_source import NewsSource
from osah.domain.entities.security_profile import SecurityProfile


@dataclass(slots=True)
class SettingsWorkspace:
    """Aggregated settings data used by the SettingsScreen."""

    security_profile: SecurityProfile
    mail_settings: MailSettings
    news_sources: tuple[NewsSource, ...]
    backup_directory_path: str
    backup_snapshot_count: int
    backup_max_copies: int
    backup_auto_enabled: bool
    ppe_warning_days: int
    news_refresh_time: str
    app_version: str
    database_path: str
    data_directory_path: str
    is_initialized: bool
