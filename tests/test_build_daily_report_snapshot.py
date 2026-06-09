import os
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from osah.application.services.build_daily_report_document import build_daily_report_document
from osah.application.services.initialize_application import initialize_application
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class BuildDailyReportSnapshotTests(unittest.TestCase):
    """Тести структури знімка щоденного звіту.
    Tests for the daily report snapshot structure.
    """

    def test_snapshot_maps_employee_problems_into_module_sections(self) -> None:
        """Перевіряє наявність п'яти секцій і секції «Без зауважень».
        Checks five sections and the no-remarks section data.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            os.environ["OSAH_ENABLE_DEMO_SEED"] = "1"
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)
            document = build_daily_report_document(
                context.database_path,
                created_at=datetime(2026, 6, 8, 10, 0),
            )
            snapshot = document.snapshot
            self.assertEqual(len(snapshot.sections), 5)
            total_problem_rows = sum(len(section.rows) for section in snapshot.sections)
            self.assertGreater(total_problem_rows, 0)
            self.assertGreater(len(snapshot.no_remarks_employees), 0)
            shut_down_logging()


if __name__ == "__main__":
    unittest.main()
