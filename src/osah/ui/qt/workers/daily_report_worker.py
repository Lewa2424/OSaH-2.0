from pathlib import Path

from PySide6.QtCore import QObject, Signal

from osah.application.services.save_daily_report_document_copy import save_daily_report_document_copy
from osah.application.services.send_daily_report_email import send_daily_report_email


class DailyReportWorker(QObject):
    """Background worker for daily report build/send operations."""

    progress = Signal(int, str)
    success = Signal(object)
    error = Signal(str)
    finished = Signal()

    def __init__(self, database_path: Path, operation_kind: str) -> None:
        super().__init__()
        self._database_path = database_path
        self._operation_kind = operation_kind

    # ###### ФОНОВА ОБРОБКА ЩОДЕННОГО ЗВІТУ / BACKGROUND DAILY REPORT PROCESS ######
    def run(self) -> None:
        """Builds report copy or sends report without blocking UI thread."""

        try:
            if self._operation_kind == "build":
                self.progress.emit(20, "Формування файлу щоденного звіту.")
                report_path = save_daily_report_document_copy(self._database_path)
                self.progress.emit(100, "Файл звіту сформовано.")
                self.success.emit({"report_path": report_path, "fallback_path": None, "operation_kind": "build"})
                return

            if self._operation_kind == "send":
                self.progress.emit(20, "Формування та відправка щоденного звіту.")
                report_path, fallback_path = send_daily_report_email(self._database_path)
                self.progress.emit(100, "Сценарій доставки звіту завершено.")
                self.success.emit(
                    {
                        "report_path": report_path,
                        "fallback_path": fallback_path,
                        "operation_kind": "send",
                    }
                )
                return

            raise ValueError(f"Непідтримуваний тип операції звіту: {self._operation_kind}")
        except Exception as error:  # noqa: BLE001
            self.error.emit(f"Операцію зі звітом зупинено: {error}")
        finally:
            self.finished.emit()
