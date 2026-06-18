import tempfile
import unittest
from pathlib import Path

from osah.application.services.ai.prepare_ai_bulk_command import prepare_ai_bulk_command
from osah.application.services.ai.prepare_ai_write_command import prepare_ai_write_command
from osah.application.services.initialize_application import initialize_application
from osah.domain.entities.ai_bulk_audience_spec import AiBulkAudienceSpec
from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.entities.ai_item_draft import AiItemDraft
from osah.domain.entities.ai_prepared_command_status import AiPreparedCommandStatus
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class AiPrepareCommandsTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self._temporary_directory.cleanup)
        application_paths = build_application_paths(Path(self._temporary_directory.name))
        initialize_application(application_paths)
        self.addCleanup(shut_down_logging)
        self._database_path = application_paths.database_file_path

    def test_prepare_single_write_returns_confirmation_view(self) -> None:
        prepared = prepare_ai_write_command(
            self._database_path,
            AiCommandDraft(
                intent=AiIntentKind.CREATE_PPE_ISSUANCE,
                raw_command="видай 0001 каску",
                source="test",
                employee_query="0001",
                items=(AiItemDraft(name="Каска", quantity=1),),
                issue_date="сьогодні",
                needs_confirmation=True,
            ),
        )

        self.assertEqual(prepared.status, AiPreparedCommandStatus.READY)
        self.assertEqual(prepared.personnel_number, "0001")
        self.assertIsNotNone(prepared.confirmation_view)

    def test_prepare_bulk_write_returns_confirmation_view(self) -> None:
        prepared = prepare_ai_bulk_command(
            self._database_path,
            AiCommandDraft(
                intent=AiIntentKind.BULK_CREATE_PPE_ISSUANCE,
                raw_command="видай співробітнику 0001 каску",
                source="test",
                bulk_audience_spec=AiBulkAudienceSpec(resolved_personnel_numbers=("0001",)),
                items=(AiItemDraft(name="Каска", quantity=1),),
                issue_date="сьогодні",
                needs_confirmation=True,
            ),
        )

        self.assertEqual(prepared.status, AiPreparedCommandStatus.READY)
        self.assertEqual(prepared.personnel_numbers, ("0001",))
        self.assertIsNotNone(prepared.confirmation_view)

    def test_prepare_bulk_without_audience_is_invalid(self) -> None:
        prepared = prepare_ai_bulk_command(
            self._database_path,
            AiCommandDraft(
                intent=AiIntentKind.BULK_CREATE_PPE_ISSUANCE,
                raw_command="видай всім каску",
                source="test",
                items=(AiItemDraft(name="Каска", quantity=1),),
                issue_date="сьогодні",
                needs_confirmation=True,
            ),
        )

        self.assertEqual(prepared.status, AiPreparedCommandStatus.INVALID)
        self.assertTrue(prepared.message)


if __name__ == "__main__":
    unittest.main()
