from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class ProgramAccessResetResult:
    """Результат налаштування або скидання доступу.
    Результат настройки или сброса доступа.
    """

    recovery_code: str
    recovery_file_path: Path
