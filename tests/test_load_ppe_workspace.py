import tempfile
import unittest
from pathlib import Path

from osah.application.services.initialize_application import initialize_application
from osah.application.services.load_ppe_workspace import load_ppe_workspace
from osah.domain.entities.ppe_status import PpeStatus
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class LoadPpeWorkspaceTests(unittest.TestCase):
    """Тести робочої моделі Qt-модуля ЗІЗ.
    Tests for the Qt PPE module workspace model.
    """

    # ###### ПЕРЕВІРКА РОБОЧОГО ПРОСТОРУ / WORKSPACE CHECK ######
    def test_load_ppe_workspace_builds_rows_and_summary(self) -> None:
        """Перевіряє, що ЗІЗ мають рядки, причини статусів і лічильники.
        Checks that PPE has rows, status reasons and counters.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)

            workspace = load_ppe_workspace(context.database_path)

            self.assertGreater(len(workspace.rows), 80)
            self.assertTrue(any(row.status_reason for row in workspace.rows))
            self.assertTrue(any(row.status == PpeStatus.NOT_ISSUED for row in workspace.rows))
            self.assertGreater(workspace.summary.not_issued_total, 0)
            shut_down_logging()


if __name__ == "__main__":
    unittest.main()
