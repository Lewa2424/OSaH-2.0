from dataclasses import dataclass
from pathlib import Path

from osah.domain.entities.dashboard_snapshot import DashboardSnapshot


@dataclass(slots=True)
class ApplicationContext:
    """Контекст ініціалізованого застосунку.
    Контекст инициализированного приложения.
    """

    database_path: Path
    log_path: Path
    dashboard_snapshot: DashboardSnapshot
