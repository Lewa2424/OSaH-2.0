from osah.domain.entities.daily_report_snapshot import DailyReportSnapshot


# ###### ТЕКСТ ЛИСТА ДЛЯ ЩОДЕННОГО ЗВІТУ / BUILD DAILY REPORT EMAIL BODY TEXT ######
def build_daily_report_email_body_text(snapshot: DailyReportSnapshot) -> str:
    """Повертає короткий текст листа зі зведенням щоденного звіту.
    Returns a short email body summarizing the daily report.
    """

    return (
        f"Щоденний звіт ClearWork за {snapshot.created_at_text}.\n"
        f"Підприємство: {snapshot.enterprise_name}\n"
        f"Працівників: {snapshot.employee_total}; критичних: {snapshot.critical_items}; "
        f"увага: {snapshot.warning_items}.\n"
        f"Фокус дня: {snapshot.focus_of_the_day}\n\n"
        "Детальний звіт у вкладенні у форматі Word (.docx)."
    )
