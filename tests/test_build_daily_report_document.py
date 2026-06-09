import os
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from osah.application.services.build_daily_report_document import build_daily_report_document
from osah.application.services.initialize_application import initialize_application
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class BuildDailyReportDocumentTests(unittest.TestCase):
    """Тести побудови щоденного звіту.
    Тесты построения ежедневного отчёта.
    """

    def test_build_daily_report_document_returns_subject_and_snapshot(self) -> None:
        """Перевіряє, що документ звіту містить тему та структурований знімок.
        Checks that the report document contains the subject and structured snapshot.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            os.environ["OSAH_ENABLE_DEMO_SEED"] = "1"
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)

            daily_report_document = build_daily_report_document(
                context.database_path,
                created_at=datetime(2026, 4, 10, 9, 30),
            )

            self.assertIn("2026-04-10", daily_report_document.subject_text)
            snapshot = daily_report_document.snapshot
            self.assertEqual(len(snapshot.sections), 5)
            self.assertEqual(
                tuple(section.title for section in snapshot.sections),
                ("Інструктажі", "ЗІЗ", "Медицина", "Наряди-допуски", "Підрядники"),
            )
            self.assertGreaterEqual(snapshot.employee_total, 1)
            self.assertTrue(snapshot.focus_of_the_day.strip())
            self.assertIsInstance(snapshot.no_remarks_employees, tuple)
            shut_down_logging()


if __name__ == "__main__":
    unittest.main()
