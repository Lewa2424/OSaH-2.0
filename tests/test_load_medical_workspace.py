import tempfile
import unittest
from pathlib import Path

from osah.application.services.initialize_application import initialize_application
from osah.application.services.load_medical_workspace import load_medical_workspace
from osah.domain.entities.medical_status import MedicalStatus
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class LoadMedicalWorkspaceTests(unittest.TestCase):
    """Тести робочої моделі Qt-модуля медицини.
    Tests for the Qt medical module workspace model.
    """

    # ###### ПЕРЕВІРКА РОБОЧОГО ПРОСТОРУ / WORKSPACE CHECK ######
    def test_load_medical_workspace_builds_rows_and_summary(self) -> None:
        """Перевіряє, що медичний модуль має рядки, причини статусів і лічильники.
        Checks that medical module has rows, status reasons and counters.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)

            workspace = load_medical_workspace(context.database_path)

            self.assertGreater(len(workspace.rows), 40)
            self.assertTrue(any(row.status_reason for row in workspace.rows))
            self.assertTrue(any(row.status in {MedicalStatus.EXPIRED, MedicalStatus.NOT_FIT} for row in workspace.rows))
            self.assertGreater(workspace.summary.critical_total, 0)
            shut_down_logging()


if __name__ == "__main__":
    unittest.main()
