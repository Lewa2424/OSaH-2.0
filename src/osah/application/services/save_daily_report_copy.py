from pathlib import Path

from osah.domain.entities.daily_report_document import DailyReportDocument


# ###### ЗБЕРЕЖЕННЯ КОПІЇ ЩОДЕННОГО ЗВІТУ / СОХРАНЕНИЕ КОПИИ ЕЖЕДНЕВНОГО ОТЧЁТА ######
def save_daily_report_copy(database_path: Path, daily_report_document: DailyReportDocument) -> Path:
    """Зберігає текстову копію щоденного звіту у локальний каталог reports.
    Сохраняет текстовую копию ежедневного отчёта в локальный каталог reports.
    """

    report_directory = database_path.parent / "reports"
    report_directory.mkdir(parents=True, exist_ok=True)
    created_at_stamp = daily_report_document.created_at_text.replace(":", "").replace("-", "").replace(" ", "-")
    report_file_path = report_directory / f"daily-report-{created_at_stamp}.txt"
    report_file_path.write_text(
        f"{daily_report_document.subject_text}\n\n{daily_report_document.body_text}",
        encoding="utf-8",
    )
    return report_file_path
