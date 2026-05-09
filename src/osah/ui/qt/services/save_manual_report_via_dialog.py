from pathlib import Path

from PySide6.QtWidgets import QFileDialog, QWidget

from osah.application.services.build_and_save_manual_daily_report import build_and_save_manual_daily_report
from osah.domain.entities.manual_report_save_result import ManualReportSaveResult
from osah.domain.services.build_manual_report_default_file_name import build_manual_report_default_file_name


# ###### ЗБЕРЕЖЕННЯ ЩОДЕННОГО ЗВІТУ ЧЕРЕЗ SAVE DIALOG / SAVE MANUAL REPORT VIA DIALOG ######
def save_manual_report_via_dialog(parent: QWidget, database_path: Path) -> ManualReportSaveResult | None:
    """Відкриває системний SaveFileDialog та зберігає щоденний звіт у вибраний файл.
    Opens the system save dialog and stores the daily report in the chosen file.
    """

    reports_directory = database_path.parent / "reports"
    suggested_path = reports_directory / build_manual_report_default_file_name()
    selected_path_text, _ = QFileDialog.getSaveFileName(
        parent,
        "Зберегти щоденний звіт",
        str(suggested_path),
        "Text files (*.txt);;All files (*)",
    )
    if not selected_path_text:
        return None
    return build_and_save_manual_daily_report(database_path, Path(selected_path_text))
