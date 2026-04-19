from datetime import datetime
from pathlib import Path

from osah.domain.entities.backup_kind import BackupKind
from osah.infrastructure.backups.build_backup_directory_path import build_backup_directory_path
from osah.infrastructure.backups.list_backup_snapshots_from_directory import list_backup_snapshots_from_directory

from osah.application.services.create_backup_snapshot import create_backup_snapshot


# ###### ЗАБЕЗПЕЧЕННЯ СТАРТОВОЇ АВТОКОПІЇ / ОБЕСПЕЧЕНИЕ СТАРТОВОЙ АВТОКОПИИ ######
def ensure_startup_auto_backup(database_path: Path, current_moment: datetime | None = None) -> Path | None:
    """Створює одну автоматичну резервну копію за поточну дату, якщо її ще немає.
    Создаёт одну автоматическую резервную копию за текущую дату, если её ещё нет.
    """

    reference_moment = current_moment or datetime.now()
    reference_date_text = reference_moment.strftime("%Y-%m-%d")
    existing_auto_snapshots = (
        backup_snapshot
        for backup_snapshot in list_backup_snapshots_from_directory(build_backup_directory_path(database_path))
        if backup_snapshot.backup_kind == BackupKind.AUTO
    )
    if any(backup_snapshot.created_at_text.startswith(reference_date_text) for backup_snapshot in existing_auto_snapshots):
        return None
    return create_backup_snapshot(database_path, BackupKind.AUTO)
