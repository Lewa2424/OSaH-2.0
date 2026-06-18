import json
import tempfile
import unittest
from pathlib import Path

from osah.application.services.ai.build_ai_explain_answer import build_ai_explain_answer
from osah.application.services.ai.build_ai_query_answer import build_ai_query_answer
from osah.application.services.ai.query_daily_focus import query_daily_focus
from osah.application.services.ai.query_employee_module_records import query_employee_module_records
from osah.application.services.ai.query_employees_by_filter import query_employees_by_filter
from osah.application.services.ai.query_overdue_summary import query_overdue_summary
from osah.application.services.ai.query_port_r_incomplete_passports import query_port_r_incomplete_passports
from osah.application.services.ai.query_work_permit_list import query_work_permit_list
from osah.application.services.ai.search_ppe_catalog_candidates import search_ppe_catalog_candidates
from osah.application.services.initialize_application import initialize_application
from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.entities.ai_ui_context import AiUiContext
from osah.domain.entities.app_section import AppSection
from osah.domain.services.ai.build_ai_navigation_target import build_ai_navigation_target
from osah.domain.services.ai.detect_duplicate_ppe_issuance import detect_duplicate_ppe_issuance
from osah.domain.services.ai.ensure_ai_intent_is_allowed import (
    is_ai_answer_intent,
    is_ai_navigation_intent,
    is_ai_write_intent,
)
from osah.domain.services.ai.map_ai_payload_to_draft import map_ai_payload_to_draft
from osah.domain.services.ai.normalize_ai_medical_decision import normalize_ai_medical_decision
from osah.domain.services.ai.normalize_ai_training_type import normalize_ai_training_type
from osah.domain.services.ai.try_match_simple_ai_command import try_match_simple_ai_command
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class AiNavigationFilterTests(unittest.TestCase):
    def test_show_overdue_uses_registry_status_values(self) -> None:
        draft = AiCommandDraft(intent=AiIntentKind.SHOW_OVERDUE, raw_command="просрочки", source="test")
        ppe_target = build_ai_navigation_target(draft, ui_context=AiUiContext(section=AppSection.PPE))
        self.assertIsNotNone(ppe_target)
        assert ppe_target is not None
        self.assertEqual(ppe_target.ppe_status_filter, "expired")


class AiIntentCategoryTests(unittest.TestCase):
    def test_new_write_intents(self) -> None:
        self.assertTrue(is_ai_write_intent(AiIntentKind.UPDATE_PPE_RECORD))
        self.assertTrue(is_ai_answer_intent(AiIntentKind.EXPLAIN_HELP))

    def test_generate_report_is_answer_not_navigation(self) -> None:
        self.assertTrue(is_ai_answer_intent(AiIntentKind.GENERATE_REPORT_TEXT))
        self.assertFalse(is_ai_navigation_intent(AiIntentKind.GENERATE_REPORT_TEXT))


class AiPayloadMappingTests(unittest.TestCase):
    def test_map_extended_payload(self) -> None:
        draft = map_ai_payload_to_draft(
            "test",
            {
                "intent": "update_employee_fields",
                "employee_query": "0001",
                "employee_field_updates": {"position_name": "Стропальник"},
                "needs_confirmation": True,
            },
        )
        self.assertEqual(draft.intent, AiIntentKind.UPDATE_EMPLOYEE_FIELDS)
        self.assertIsNotNone(draft.employee_field_updates)
        assert draft.employee_field_updates is not None
        self.assertEqual(draft.employee_field_updates.position_name, "Стропальник")


class AiNormalizeTests(unittest.TestCase):
    def test_training_type_aliases(self) -> None:
        self.assertEqual(normalize_ai_training_type("повторний"), "repeated")

    def test_medical_decision_aliases(self) -> None:
        self.assertEqual(normalize_ai_medical_decision("придатний"), "fit")


class AiQueryServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self._temporary_directory.cleanup)
        self._application_paths = build_application_paths(Path(self._temporary_directory.name))
        initialize_application(self._application_paths)
        self.addCleanup(shut_down_logging)
        self._database_path = self._application_paths.database_file_path

    def test_search_ppe_catalog_candidates_uses_defaults(self) -> None:
        candidates = search_ppe_catalog_candidates(self._database_path, "каска")
        self.assertTrue(any("каск" in candidate.lower() for candidate in candidates))

    def test_query_daily_focus_returns_text(self) -> None:
        result = query_daily_focus(self._database_path)
        self.assertTrue(result.focus_text)

    def test_query_overdue_summary_includes_warnings(self) -> None:
        summary = query_overdue_summary(self._database_path)
        self.assertGreaterEqual(summary.ppe_warning, 0)

    def test_build_missing_ppe_empty_catalog_message(self) -> None:
        draft = AiCommandDraft(
            intent=AiIntentKind.QUERY_MISSING_PPE,
            raw_command="test",
            source="test",
            ppe_item_query="nonexistent-item-xyz",
        )
        answer = build_ai_query_answer(self._database_path, draft)
        self.assertIsNotNone(answer)
        assert answer is not None
        self.assertIn("каталозі", answer.text.lower())

    def test_query_employee_records_and_filters(self) -> None:
        rows = query_employee_module_records(self._database_path, personnel_number="0001", module_key="ppe")
        self.assertIsInstance(rows, tuple)
        employees = query_employees_by_filter(self._database_path, "active")
        self.assertIsInstance(employees, tuple)
        warning_rows = query_employees_by_filter(self._database_path, "warning")
        self.assertIsInstance(warning_rows, tuple)
        self.assertTrue(any(row.employment_status for row in warning_rows))

    def test_work_permit_and_port_r_queries(self) -> None:
        permits = query_work_permit_list(self._database_path, "open")
        self.assertIsInstance(permits, tuple)
        gaps = query_port_r_incomplete_passports(self._database_path)
        self.assertIsInstance(gaps, tuple)

    def test_explain_help_domain(self) -> None:
        draft = AiCommandDraft(
            intent=AiIntentKind.EXPLAIN_HELP,
            raw_command="Що таке цільовий інструктаж?",
            source="test",
            explain_topic="domain",
        )
        answer = build_ai_explain_answer(self._database_path, draft)
        self.assertIn("інструктаж", answer.lower())


class AiDuplicateDetectionTests(unittest.TestCase):
    def test_detect_duplicate_without_records_is_false(self) -> None:
        temporary_directory = tempfile.TemporaryDirectory()
        try:
            application_paths = build_application_paths(Path(temporary_directory.name))
            initialize_application(application_paths)
            self.assertFalse(
                detect_duplicate_ppe_issuance(
                    application_paths.database_file_path,
                    personnel_number="9999",
                    ppe_name="Каска захисна",
                    issue_date_text="сьогодні",
                )
            )
        finally:
            shut_down_logging()
            temporary_directory.cleanup()


class AiGoldenSetQueryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        fixture_path = Path(__file__).resolve().parent / "fixtures" / "ai_command_golden_set.json"
        cls._golden_entries = json.loads(fixture_path.read_text(encoding="utf-8"))

    def test_golden_set_minimum_size(self) -> None:
        self.assertGreaterEqual(len(self._golden_entries), 100)

    def test_router_entries_match(self) -> None:
        for entry in self._golden_entries:
            if not entry.get("router_should_match"):
                continue
            draft = try_match_simple_ai_command(entry["command"])
            self.assertIsNotNone(draft, msg=entry["command"])
            assert draft is not None
            self.assertEqual(draft.intent.value, entry["expected_intent"], msg=entry["command"])


if __name__ == "__main__":
    unittest.main()
