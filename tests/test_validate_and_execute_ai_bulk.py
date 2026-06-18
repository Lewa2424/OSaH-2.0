import tempfile
import unittest
from pathlib import Path

from osah.application.services.ai.execute_confirmed_ai_bulk_command import execute_confirmed_ai_bulk_command
from osah.application.services.initialize_application import initialize_application
from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.entities.ai_item_draft import AiItemDraft
from osah.domain.services.ai.validate_ai_bulk_operation import collect_ai_bulk_blocking_issues, validate_ai_bulk_operation
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class ValidateBulkOperationTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self._temporary_directory.cleanup)
        self._application_paths = build_application_paths(Path(self._temporary_directory.name))
        initialize_application(self._application_paths)
        self.addCleanup(shut_down_logging)
        self._database_path = self._application_paths.database_file_path

    def test_validate_returns_rows(self) -> None:
        draft = AiCommandDraft(
            intent=AiIntentKind.BULK_CREATE_PPE_ISSUANCE,
            raw_command="test",
            source="test",
            issue_date="сьогодні",
            items=(AiItemDraft(name="Каска", quantity=1),),
        )
        rows = validate_ai_bulk_operation(self._database_path, draft, ("0001",))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].personnel_number, "0001")

    def test_medical_missing_decision_blocks(self) -> None:
        draft = AiCommandDraft(
            intent=AiIntentKind.BULK_CREATE_MEDICAL_RECORD,
            raw_command="test",
            source="test",
            issue_date="сьогодні",
        )
        issues = collect_ai_bulk_blocking_issues(self._database_path, draft, ("0001",))
        self.assertTrue(issues)


class ExecuteBulkCommandTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self._temporary_directory.cleanup)
        self._application_paths = build_application_paths(Path(self._temporary_directory.name))
        initialize_application(self._application_paths)
        self.addCleanup(shut_down_logging)
        self._database_path = self._application_paths.database_file_path

    def test_bulk_training_smoke(self) -> None:
        draft = AiCommandDraft(
            intent=AiIntentKind.BULK_CREATE_TRAINING_RECORD,
            raw_command="test",
            source="test",
            issue_date="сьогодні",
            training_type="repeated",
            next_control_date="31.12.2026",
            conducted_by="Інспектор",
        )
        message = execute_confirmed_ai_bulk_command(
            self._database_path,
            draft,
            personnel_numbers=("0001",),
            access_role=AccessRole.INSPECTOR,
        )
        self.assertIn("1", message)


if __name__ == "__main__":
    unittest.main()
