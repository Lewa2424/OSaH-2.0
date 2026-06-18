import tempfile
import unittest
from pathlib import Path

from osah.application.services.ai.resolve_ai_bulk_audience import resolve_ai_bulk_audience
from osah.application.services.initialize_application import initialize_application
from osah.domain.entities.ai_bulk_audience_resolution_status import AiBulkAudienceResolutionStatus
from osah.domain.entities.ai_bulk_audience_spec import AiBulkAudienceSpec
from osah.domain.entities.ai_bulk_limits import AI_BULK_MAX_AUDIENCE_SIZE
from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.services.ai.has_bulk_audience_narrowing import has_bulk_audience_narrowing
from osah.domain.services.ai.reconcile_ai_command_draft import reconcile_ai_command_draft
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class HasBulkAudienceNarrowingTests(unittest.TestCase):
    def test_active_only_is_not_narrowing(self) -> None:
        spec = AiBulkAudienceSpec(filter_key="active")
        self.assertFalse(has_bulk_audience_narrowing(spec))

    def test_department_is_narrowing(self) -> None:
        spec = AiBulkAudienceSpec(filter_key="active", department_query="N2")
        self.assertTrue(has_bulk_audience_narrowing(spec))


class ReconcileBulkTests(unittest.TestCase):
    def test_bulk_ppe_promoted_with_clarification_without_narrowing(self) -> None:
        draft = reconcile_ai_command_draft(
            AiCommandDraft(
                intent=AiIntentKind.CREATE_PPE_ISSUANCE,
                raw_command="Додай всім каски",
                source="llm",
            )
        )
        self.assertEqual(draft.intent, AiIntentKind.BULK_CREATE_PPE_ISSUANCE)
        self.assertIsNotNone(draft.clarification_message)

    def test_bulk_training_with_department_narrowing(self) -> None:
        draft = reconcile_ai_command_draft(
            AiCommandDraft(
                intent=AiIntentKind.CREATE_TRAINING_RECORD,
                raw_command="Занеси повторний інструктаж усім стропальникам дільниці N2",
                source="llm",
                issue_date="сьогодні",
            )
        )
        self.assertEqual(draft.intent, AiIntentKind.BULK_CREATE_TRAINING_RECORD)
        self.assertIsNone(draft.clarification_message)
        self.assertIsNotNone(draft.bulk_audience_spec)
        assert draft.bulk_audience_spec is not None
        self.assertEqual(draft.bulk_audience_spec.department_query, "N2")


class ResolveBulkAudienceTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self._temporary_directory.cleanup)
        self._application_paths = build_application_paths(Path(self._temporary_directory.name))
        initialize_application(self._application_paths)
        self.addCleanup(shut_down_logging)
        self._database_path = self._application_paths.database_file_path

    def test_filter_active_with_department_resolves(self) -> None:
        draft = AiCommandDraft(
            intent=AiIntentKind.BULK_CREATE_PPE_ISSUANCE,
            raw_command="test",
            source="test",
            bulk_audience_spec=AiBulkAudienceSpec(filter_key="active", department_query="вироб"),
            issue_date="сьогодні",
            items=(),
        )
        resolution = resolve_ai_bulk_audience(self._database_path, draft)
        self.assertIn(
            resolution.status,
            {
                AiBulkAudienceResolutionStatus.READY,
                AiBulkAudienceResolutionStatus.EMPTY,
            },
        )

    def test_department_matching_tolerates_ru_ua_spelling(self) -> None:
        draft = AiCommandDraft(
            intent=AiIntentKind.BULK_CREATE_PPE_ISSUANCE,
            raw_command="test",
            source="test",
            bulk_audience_spec=AiBulkAudienceSpec(department_query="Энергетическая служба"),
            issue_date="сегодня",
            items=(),
        )
        resolution = resolve_ai_bulk_audience(self._database_path, draft)
        self.assertEqual(resolution.status, AiBulkAudienceResolutionStatus.READY)
        self.assertTrue(resolution.personnel_numbers)

    def test_cap_returns_too_large(self) -> None:
        huge_set = frozenset(str(index).zfill(4) for index in range(AI_BULK_MAX_AUDIENCE_SIZE + 1))
        draft = AiCommandDraft(
            intent=AiIntentKind.BULK_UPDATE_EMPLOYEE_FIELDS,
            raw_command="test",
            source="test",
            bulk_audience_spec=AiBulkAudienceSpec(resolved_personnel_numbers=tuple(huge_set)),
        )
        resolution = resolve_ai_bulk_audience(self._database_path, draft)
        self.assertEqual(resolution.status, AiBulkAudienceResolutionStatus.TOO_LARGE)

    def test_position_query_narrowing(self) -> None:
        draft = reconcile_ai_command_draft(
            AiCommandDraft(
                intent=AiIntentKind.CREATE_PPE_ISSUANCE,
                raw_command="выдай всем в должности электромонтера перчатки",
                source="llm",
                issue_date="сьогодні",
                items=(),
            )
        )
        self.assertEqual(draft.intent, AiIntentKind.BULK_CREATE_PPE_ISSUANCE)
        assert draft.bulk_audience_spec is not None
        self.assertEqual(draft.bulk_audience_spec.position_query, "электромонтера")

    def test_department_in_ceh_span(self) -> None:
        draft = reconcile_ai_command_draft(
            AiCommandDraft(
                intent=AiIntentKind.CREATE_PPE_ISSUANCE,
                raw_command="выдай всем в цеху механоскладальный каски",
                source="llm",
                issue_date="сьогодні",
                items=(),
            )
        )
        assert draft.bulk_audience_spec is not None
        self.assertEqual(draft.bulk_audience_spec.department_query, "механоскладальный")


if __name__ == "__main__":
    unittest.main()
