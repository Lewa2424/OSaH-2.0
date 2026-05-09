from osah.domain.entities.manual_report_settings import ManualReportSettings


# ###### ПОБУДОВА ТЕКСТУ ПРО ОСТАННЮ ДІЮ ЗІ ЗВІТОМ / BUILD MANUAL REPORT LAST ACTION TEXT ######
def build_manual_report_last_action_text(manual_report_settings: ManualReportSettings) -> str:
    """Повертає короткий текст про останню дію користувача зі щоденним звітом.
    Returns a short text describing the latest user action for the daily report.
    """

    if manual_report_settings.last_generated_date:
        return f"сформовано {manual_report_settings.last_generated_date}"
    if manual_report_settings.last_skipped_date:
        return f"пропущено {manual_report_settings.last_skipped_date}"
    return "ще не виконувалось"
