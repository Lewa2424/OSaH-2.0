from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class ManualReportSaveResult:
    """Результат ручного формування та збереження щоденного звіту.
    Result of manual daily report generation and saving.
    """

    user_file_path: Path
    internal_copy_path: Path
    created_at_text: str
