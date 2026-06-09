from pathlib import Path

from osah.domain.entities.daily_report_document import DailyReportDocument
from osah.infrastructure.docx.render_daily_report_docx import render_daily_report_docx


# ###### ЗБЕРЕЖЕННЯ КОПІЇ ЩОДЕННОГО ЗВІТУ / СОХРАНЕНИЕ КОПИИ ЕЖЕДНЕВНОГО ОТЧЁТА ######
def save_daily_report_copy(database_path: Path, daily_report_document: DailyReportDocument) -> Path:
    """Зберігає копію щоденного звіту у форматі .docx у локальний каталог reports.
    Saves a .docx copy of the daily report into the local reports directory.
    """

    report_directory = database_path.parent / "reports"
    report_directory.mkdir(parents=True, exist_ok=True)
    created_at_stamp = daily_report_document.created_at_text.replace(":", "").replace("-", "").replace(" ", "-")
    report_file_path = report_directory / f"daily-report-{created_at_stamp}.docx"
    return render_daily_report_docx(daily_report_document.snapshot, report_file_path)
