import tempfile
import unittest
from pathlib import Path

from osah.application.services.initialize_application import initialize_application
from osah.application.services.load_employee_workspace import load_employee_workspace
from osah.domain.entities.employee_status_level import EmployeeStatusLevel
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class LoadEmployeeWorkspaceTests(unittest.TestCase):
    """Тести робочої моделі Qt-екрана працівників.
    Tests for the employees Qt screen workspace model.
    """

    # ###### ПЕРЕВІРКА РОБОЧОГО ПРОСТОРУ / WORKSPACE CHECK ######
    def test_load_employee_workspace_builds_rows_with_statuses(self) -> None:
        """Перевіряє, що сервіс збирає працівників, модульні статуси і причини.
        Checks that the service builds employees, module statuses and reasons.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)

            workspace = load_employee_workspace(context.database_path)

            self.assertGreaterEqual(len(workspace.rows), 50)
            self.assertTrue(workspace.enterprise_name)
            self.assertTrue(all(len(row.module_summaries) == 4 for row in workspace.rows))
            self.assertTrue(any(row.problems for row in workspace.rows))
            self.assertTrue(any(row.status_level == EmployeeStatusLevel.CRITICAL for row in workspace.rows))
            shut_down_logging()


if __name__ == "__main__":
    unittest.main()
