from pathlib import Path

from osah.application.services.load_manual_report_settings import load_manual_report_settings


# ###### ПОШУК ОСТАННЬОГО ЗБЕРЕЖЕНОГО ФАЙЛУ ЗВІТУ / LOAD LATEST MANUAL REPORT FILE PATH ######
def load_latest_manual_report_file_path(database_path: Path) -> Path | None:
    """Повертає шлях до останнього збереженого щоденного звіту або None.
    Returns the path to the latest saved daily report file or None.
    """

    manual_report_settings = load_manual_report_settings(database_path)
    if manual_report_settings.last_saved_file_path.strip():
        saved_path = Path(manual_report_settings.last_saved_file_path)
        if saved_path.is_file():
            return saved_path

    report_directory = database_path.parent / "reports"
    if not report_directory.exists():
        return None

    report_paths = tuple(
        path
        for pattern in ("daily-report-*.docx", "ClearWork_*.docx")
        for path in report_directory.glob(pattern)
        if path.is_file()
    )
    if not report_paths:
        return None
    return max(report_paths, key=lambda path: path.stat().st_mtime)
