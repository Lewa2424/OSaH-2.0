from osah.domain.entities.backup_snapshot import BackupSnapshot
from osah.ui.desktop.content.settings.format_backup_kind_label import format_backup_kind_label


# ###### ПОБУДОВА ОПЦІЙ РЕЗЕРВНИХ КОПІЙ / ПОСТРОЕНИЕ ОПЦИЙ РЕЗЕРВНЫХ КОПИЙ ######
def build_backup_snapshot_options(backup_snapshots: tuple[BackupSnapshot, ...]) -> tuple[str, ...]:
    """Повертає підписи резервних копій для вибору у формі відновлення.
    Возвращает подписи резервных копий для выбора в форме восстановления.
    """

    return tuple(
        f"{backup_snapshot.file_name} | {format_backup_kind_label(backup_snapshot.backup_kind)} | {backup_snapshot.created_at_text}"
        for backup_snapshot in backup_snapshots
    )
