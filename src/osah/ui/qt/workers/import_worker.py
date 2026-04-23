from pathlib import Path

from PySide6.QtCore import QObject, Signal

from osah.application.services.apply_employee_import_batch import apply_employee_import_batch
from osah.application.services.create_employee_import_batch_from_file import create_employee_import_batch_from_file


class ImportWorker(QObject):
    """Background worker for employee import flow operations."""

    progress = Signal(int, str)
    success = Signal(object)
    error = Signal(str)
    finished = Signal()

    def __init__(
        self,
        database_path: Path,
        operation_kind: str,
        source_file_path: Path | None = None,
        batch_id: int | None = None,
    ) -> None:
        super().__init__()
        self._database_path = database_path
        self._operation_kind = operation_kind
        self._source_file_path = source_file_path
        self._batch_id = batch_id

    # ###### ФОНОВІ ОПЕРАЦІЇ ІМПОРТУ / BACKGROUND IMPORT OPERATIONS ######
    def run(self) -> None:
        """Runs import draft creation or import batch apply outside UI thread."""

        try:
            if self._operation_kind == "create_batch":
                if self._source_file_path is None:
                    raise ValueError("Не передано файл для створення партії імпорту.")
                self.progress.emit(10, "Читання файлу імпорту та побудова чернеток.")
                batch_id = create_employee_import_batch_from_file(self._database_path, self._source_file_path)
                self.progress.emit(100, "Партію чернеток імпорту створено.")
                self.success.emit({"operation_kind": "create_batch", "batch_id": batch_id})
                return

            if self._operation_kind == "apply_batch":
                if self._batch_id is None:
                    raise ValueError("Не передано ідентифікатор партії імпорту.")
                self.progress.emit(10, "Застосування валідних чернеток до бойових записів.")
                apply_employee_import_batch(self._database_path, self._batch_id)
                self.progress.emit(100, "Партію імпорту застосовано.")
                self.success.emit({"operation_kind": "apply_batch", "batch_id": self._batch_id})
                return

            raise ValueError(f"Непідтримуваний тип операції імпорту: {self._operation_kind}")
        except Exception as error:  # noqa: BLE001
            self.error.emit(f"Операція імпорту зупинена: {error}")
        finally:
            self.finished.emit()
