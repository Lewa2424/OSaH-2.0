import tempfile
import unittest
from pathlib import Path

from osah.application.services.initialize_application import initialize_application
from osah.application.services.load_work_permit_workspace import load_work_permit_workspace
from osah.domain.entities.work_permit_status import WorkPermitStatus
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class LoadWorkPermitWorkspaceTests(unittest.TestCase):
    """Тести робочої моделі Qt-модуля нарядів-допусків.
    Tests for the Qt work permits module workspace model.
    """

    # ###### ПЕРЕВІРКА РОБОЧОГО ПРОСТОРУ / WORKSPACE CHECK ######
    def test_load_work_permit_workspace_builds_rows_and_summary(self) -> None:
        """Перевіряє, що модуль нарядів має рядки, причини статусів і лічильники.
        Checks that work permits module has rows, status reasons and counters.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)

            workspace = load_work_permit_workspace(context.database_path)

            self.assertGreater(len(workspace.rows), 5)
            self.assertTrue(any(row.status_reason for row in workspace.rows))
            self.assertTrue(any(row.status in {WorkPermitStatus.ACTIVE, WorkPermitStatus.WARNING, WorkPermitStatus.EXPIRED} for row in workspace.rows))
            self.assertGreater(workspace.summary.total_rows, 0)
            self.assertGreater(workspace.summary.active_participants_total, 0)
            shut_down_logging()


if __name__ == "__main__":
    unittest.main()
