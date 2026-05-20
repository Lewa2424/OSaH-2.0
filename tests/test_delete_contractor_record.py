import tempfile
import unittest
from pathlib import Path

from osah.application.services.delete_contractor_record import delete_contractor_record
from osah.application.services.initialize_application import initialize_application
from osah.application.services.load_contractor_workspace import load_contractor_workspace
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class DeleteContractorRecordTests(unittest.TestCase):
    """Тести видалення запису підрядника.
    Tests contractor record deletion.
    """

    def test_delete_contractor_record_removes_record_from_registry(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            context = initialize_application(build_application_paths(Path(temporary_directory)))
            workspace_before = load_contractor_workspace(context.database_path)
            target_id = workspace_before.records[0].contractor_id

            delete_contractor_record(context.database_path, target_id)

            workspace_after = load_contractor_workspace(context.database_path)
            self.assertEqual(len(workspace_after.records), len(workspace_before.records) - 1)
            self.assertNotIn(target_id, {record.contractor_id for record in workspace_after.records})
            shut_down_logging()


if __name__ == "__main__":
    unittest.main()
