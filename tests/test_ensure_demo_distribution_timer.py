import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

from osah.application.services.initialize_application import initialize_application
from osah.application.services.security.load_demo_distribution_state import load_demo_distribution_state
from osah.application.services.security.security_setting_keys import (
    DEMO_DISTRIBUTION_ENABLED,
    DEMO_EXPIRES_AT,
    DEMO_STARTED_AT,
)
from osah.domain.services.demo_distribution_duration_hours import DEMO_DISTRIBUTION_DURATION_HOURS
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.list_app_settings import list_app_settings
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class EnsureDemoDistributionTimerTests(unittest.TestCase):
    """Тести запуску та ідемпотентності 48-годинного demo-таймера."""

    def test_initialize_starts_timer_when_timed_marker_present(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            project_root = Path(temporary_directory)
            (project_root / "ClearWork.demo").write_text("demo", encoding="utf-8")
            (project_root / "ClearWork.demo_timed").write_text("timed", encoding="utf-8")
            application_paths = build_application_paths(project_root)
            context = initialize_application(application_paths)

            connection = create_database_connection(context.database_path)
            try:
                app_settings = list_app_settings(connection)
            finally:
                connection.close()

            self.assertEqual(app_settings.get(DEMO_DISTRIBUTION_ENABLED), "1")
            self.assertTrue(app_settings.get(DEMO_STARTED_AT, "").strip())
            self.assertTrue(app_settings.get(DEMO_EXPIRES_AT, "").strip())
            shut_down_logging()

    def test_timer_initialization_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            project_root = Path(temporary_directory)
            (project_root / "ClearWork.demo").write_text("demo", encoding="utf-8")
            (project_root / "ClearWork.demo_timed").write_text("timed", encoding="utf-8")
            application_paths = build_application_paths(project_root)
            first_context = initialize_application(application_paths)

            connection = create_database_connection(first_context.database_path)
            try:
                first_settings = list_app_settings(connection)
            finally:
                connection.close()
            shut_down_logging()

            second_context = initialize_application(application_paths)
            connection = create_database_connection(second_context.database_path)
            try:
                second_settings = list_app_settings(connection)
            finally:
                connection.close()
            shut_down_logging()

            self.assertEqual(first_settings[DEMO_STARTED_AT], second_settings[DEMO_STARTED_AT])
            self.assertEqual(first_settings[DEMO_EXPIRES_AT], second_settings[DEMO_EXPIRES_AT])

    def test_load_state_marks_expired_after_deadline(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            project_root = Path(temporary_directory)
            (project_root / "ClearWork.demo_timed").write_text("timed", encoding="utf-8")
            application_paths = build_application_paths(project_root)
            context = initialize_application(application_paths)
            shut_down_logging()

            started_at = datetime.now().replace(microsecond=0) - timedelta(hours=DEMO_DISTRIBUTION_DURATION_HOURS + 1)
            expires_at = started_at + timedelta(hours=DEMO_DISTRIBUTION_DURATION_HOURS)
            connection = create_database_connection(context.database_path)
            try:
                from osah.infrastructure.database.commands.upsert_app_settings_batch import upsert_app_settings_batch

                upsert_app_settings_batch(
                    connection,
                    {
                        DEMO_STARTED_AT: started_at.isoformat(timespec="seconds"),
                        DEMO_EXPIRES_AT: expires_at.isoformat(timespec="seconds"),
                    },
                )
                connection.commit()
            finally:
                connection.close()

            demo_state = load_demo_distribution_state(context.database_path)
            self.assertTrue(demo_state.is_active)
            self.assertTrue(demo_state.is_expired)


if __name__ == "__main__":
    unittest.main()
