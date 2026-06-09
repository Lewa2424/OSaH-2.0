import os
import tempfile
import unittest
from pathlib import Path

from osah.application.services.initialize_application import initialize_application
from osah.application.services.load_employee_workspace import load_employee_workspace
from osah.domain.entities.employee_status_level import EmployeeStatusLevel
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class DemoEmployeeScenarioDistributionTests(unittest.TestCase):
    """Тести розподілу статусів після квотного демо-засіву.
    Tests for status distribution after quota-based demo seeding.
    """

    def test_demo_seed_keeps_critical_and_warning_within_expected_range(self) -> None:
        """Перевіряє, що критичних і попереджувальних статусів не надто багато.
        Checks that critical and warning statuses stay within expected bounds.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            os.environ["OSAH_ENABLE_DEMO_SEED"] = "1"
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)
            workspace = load_employee_workspace(context.database_path)

            critical_total = sum(
                1 for row in workspace.rows if row.status_level == EmployeeStatusLevel.CRITICAL
            )
            warning_total = sum(
                1 for row in workspace.rows if row.status_level == EmployeeStatusLevel.WARNING
            )
            normal_total = sum(
                1 for row in workspace.rows if row.status_level == EmployeeStatusLevel.NORMAL
            )
            restricted_total = sum(
                1 for row in workspace.rows if row.status_level == EmployeeStatusLevel.RESTRICTED
            )

            self.assertGreaterEqual(critical_total, 8)
            self.assertLessEqual(critical_total, 14)
            self.assertGreaterEqual(warning_total, 8)
            self.assertLessEqual(warning_total, 14)
            self.assertGreaterEqual(normal_total, 15)
            self.assertGreaterEqual(restricted_total, 5)
            shut_down_logging()


if __name__ == "__main__":
    unittest.main()
