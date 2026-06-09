from dataclasses import dataclass


@dataclass(slots=True)
class ManualReportSettings:
    """Налаштування ручного формування щоденного звіту.
    Settings for manual daily report generation.
    """

    manual_reminder_enabled: bool
    manual_reminder_time: str
    last_generated_date: str
    last_skipped_date: str
    next_prompt_at: str = ""
    default_save_directory: str = ""
    ask_save_path_each_time: bool = True
    last_saved_file_path: str = ""
