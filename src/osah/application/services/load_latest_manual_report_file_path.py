from pathlib import Path


# ###### ПОШУК ОСТАННЬОГО ЗБЕРЕЖЕНОГО ФАЙЛУ ЗВІТУ / LOAD LATEST MANUAL REPORT FILE PATH ######
def load_latest_manual_report_file_path(database_path: Path) -> Path | None:
    """Повертає шлях до останньої внутрішньої копії щоденного звіту або None.
    Returns the path to the latest internal daily report copy or None.
    """

    report_directory = database_path.parent / "reports"
    if not report_directory.exists():
        return None

    report_paths = tuple(
        path
        for path in report_directory.glob("daily-report-*.txt")
        if path.is_file()
    )
    if not report_paths:
        return None
    return max(report_paths, key=lambda path: path.stat().st_mtime)
