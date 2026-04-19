from dataclasses import dataclass
from pathlib import Path

from osah.domain.entities.backup_kind import BackupKind


@dataclass(slots=True)
class BackupSnapshot:
    """Опис резервної копії для списку та відновлення.
    Описание резервной копии для списка и восстановления.
    """

    file_name: str
    file_path: Path
    backup_kind: BackupKind
    created_at_text: str
    size_bytes: int
