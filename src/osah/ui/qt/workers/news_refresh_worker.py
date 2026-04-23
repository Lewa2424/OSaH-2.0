from pathlib import Path

from PySide6.QtCore import QObject, Signal

from osah.application.services.refresh_news_sources import refresh_news_sources


class NewsRefreshWorker(QObject):
    """Background worker for trusted sources refresh."""

    progress = Signal(int, str)
    success = Signal(object)
    error = Signal(str)
    finished = Signal()

    def __init__(self, database_path: Path) -> None:
        super().__init__()
        self._database_path = database_path

    # ###### ФОНОВЕ ОНОВЛЕННЯ НПА/НОВИН / BACKGROUND NEWS REFRESH ######
    def run(self) -> None:
        """Refreshes trusted sources and emits result count."""

        try:
            self.progress.emit(10, "Перевірка довірених джерел запущена.")
            cached_total = refresh_news_sources(self._database_path)
            self.progress.emit(100, "Перевірка джерел завершена.")
            self.success.emit(cached_total)
        except Exception as error:  # noqa: BLE001
            self.error.emit(f"Не вдалося оновити джерела: {error}")
        finally:
            self.finished.emit()
