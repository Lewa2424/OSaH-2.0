import tempfile
import unittest
from pathlib import Path

from osah.application.services.ai.dispatch_ai_parsed_command import dispatch_ai_parsed_command
from osah.application.services.initialize_application import initialize_application
from osah.domain.entities.ai_bulk_audience_spec import AiBulkAudienceSpec
from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_dispatch_result_kind import AiDispatchResultKind
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.entities.ai_item_draft import AiItemDraft
from osah.domain.entities.app_section import AppSection
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class AiDispatchParsedCommandTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self._temporary_directory.cleanup)
        application_paths = build_application_paths(Path(self._temporary_directory.name))
        initialize_application(application_paths)
        self.addCleanup(shut_down_logging)
        self._database_path = application_paths.database_file_path

    def test_navigation_command_returns_navigation_target(self) -> None:
        result = dispatch_ai_parsed_command(
            self._database_path,
            AiCommandDraft(
                intent=AiIntentKind.NAVIGATE_SECTION,
                raw_command="відкрий ЗІЗ",
                source="test",
                section_key="ppe",
            ),
        )

        self.assertEqual(result.kind, AiDispatchResultKind.NAVIGATION_READY)
        self.assertIsNotNone(result.navigation_target)
        assert result.navigation_target is not None
        self.assertEqual(result.navigation_target.section, AppSection.PPE)

    def test_answer_command_returns_answer_text(self) -> None:
        result = dispatch_ai_parsed_command(
            self._database_path,
            AiCommandDraft(
                intent=AiIntentKind.QUERY_DAILY_FOCUS,
                raw_command="що сьогодні важливо",
                source="test",
            ),
        )

        self.assertEqual(result.kind, AiDispatchResultKind.ANSWER_READY)
        self.assertTrue(result.answer_text)
        self.assertTrue(result.pending_answer_mode)

    def test_single_write_is_passed_to_existing_write_flow(self) -> None:
        result = dispatch_ai_parsed_command(
            self._database_path,
            AiCommandDraft(
                intent=AiIntentKind.CREATE_PPE_ISSUANCE,
                raw_command="занеси Петрову каску",
                source="test",
                employee_query="Петров",
                items=(AiItemDraft(name="каска", quantity=1),),
                issue_date="сьогодні",
                needs_confirmation=True,
            ),
        )

        self.assertEqual(result.kind, AiDispatchResultKind.WRITE_REQUIRED)
        self.assertIsNotNone(result.draft)

    def test_bulk_write_is_passed_to_existing_bulk_flow(self) -> None:
        result = dispatch_ai_parsed_command(
            self._database_path,
            AiCommandDraft(
                intent=AiIntentKind.BULK_CREATE_PPE_ISSUANCE,
                raw_command="видай складу рукавиці",
                source="test",
                bulk_audience_spec=AiBulkAudienceSpec(department_query="Склад"),
                items=(AiItemDraft(name="рукавиці", quantity=1),),
                issue_date="сьогодні",
                needs_confirmation=True,
            ),
        )

        self.assertEqual(result.kind, AiDispatchResultKind.BULK_REQUIRED)
        self.assertIsNotNone(result.draft)

    def test_unknown_intent_is_unsupported(self) -> None:
        result = dispatch_ai_parsed_command(
            self._database_path,
            AiCommandDraft(
                intent=AiIntentKind.UNKNOWN,
                raw_command="зроби щось",
                source="test",
            ),
        )

        self.assertEqual(result.kind, AiDispatchResultKind.UNSUPPORTED)
        self.assertTrue(result.message)


if __name__ == "__main__":
    unittest.main()
