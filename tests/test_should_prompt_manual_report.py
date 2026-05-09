from datetime import datetime
from pathlib import Path
import tempfile
import unittest

from osah.application.services.initialize_application import initialize_application
from osah.application.services.save_manual_report_settings import save_manual_report_settings
from osah.domain.entities.manual_report_settings import ManualReportSettings
from osah.domain.services.should_prompt_manual_report import should_prompt_manual_report
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class ShouldPromptManualReportTests(unittest.TestCase):
    """Тести логіки показу нагадування про щоденний звіт.
    Tests for the reminder logic of the manual daily report workflow.
    """

    def test_should_prompt_manual_report_when_time_due(self) -> None:
        """Перевіряє показ нагадування після настання заданого часу.
        Checks that the reminder is shown after the configured time.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            database_path = _initialize_database(Path(temporary_directory))
            save_manual_report_settings(database_path, _settings(enabled=True, reminder_time="08:00"))

            self.assertTrue(should_prompt_manual_report(database_path, datetime(2026, 5, 9, 8, 0)))
            shut_down_logging()

    def test_should_not_prompt_if_report_already_generated_today(self) -> None:
        """Перевіряє відсутність нагадування після формування звіту за сьогодні.
        Checks that no reminder is shown after today's report was generated.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            database_path = _initialize_database(Path(temporary_directory))
            save_manual_report_settings(
                database_path,
                _settings(enabled=True, reminder_time="08:00", last_generated_date="2026-05-09"),
            )

            self.assertFalse(should_prompt_manual_report(database_path, datetime(2026, 5, 9, 10, 0)))
            shut_down_logging()

    def test_should_not_prompt_if_report_skipped_today(self) -> None:
        """Перевіряє відсутність нагадування після пропуску на поточний день.
        Checks that no reminder is shown after skipping the report for today.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            database_path = _initialize_database(Path(temporary_directory))
            save_manual_report_settings(
                database_path,
                _settings(enabled=True, reminder_time="08:00", last_skipped_date="2026-05-09"),
            )

            self.assertFalse(should_prompt_manual_report(database_path, datetime(2026, 5, 9, 10, 0)))
            shut_down_logging()

    def test_should_not_prompt_before_configured_time(self) -> None:
        """Перевіряє, що нагадування не з'являється раніше заданого часу.
        Checks that the reminder does not appear before the configured time.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            database_path = _initialize_database(Path(temporary_directory))
            save_manual_report_settings(database_path, _settings(enabled=True, reminder_time="08:00"))

            self.assertFalse(should_prompt_manual_report(database_path, datetime(2026, 5, 9, 7, 59)))
            shut_down_logging()


def _initialize_database(temporary_root: Path) -> Path:
    """Повертає шлях до ініціалізованої тестової бази даних.
    Returns the path to an initialized test database.
    """

    application_paths = build_application_paths(temporary_root)
    return initialize_application(application_paths).database_path


def _settings(
    *,
    enabled: bool,
    reminder_time: str,
    last_generated_date: str = "",
    last_skipped_date: str = "",
) -> ManualReportSettings:
    """Повертає базові налаштування ручного щоденного звіту для тестів.
    Returns baseline manual daily report settings for tests.
    """

    return ManualReportSettings(
        manual_reminder_enabled=enabled,
        manual_reminder_time=reminder_time,
        last_generated_date=last_generated_date,
        last_skipped_date=last_skipped_date,
        next_prompt_at="",
        default_save_directory="",
        ask_save_path_each_time=True,
    )


if __name__ == "__main__":
    unittest.main()
