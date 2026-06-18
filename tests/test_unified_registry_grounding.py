import os
import tempfile
import unittest
from pathlib import Path

from osah.application.services.ai.apply_grounding_bulk_audience_choice import apply_grounding_bulk_audience_choice
from osah.application.services.ai.ground_ai_command_draft import ground_ai_command_draft
from osah.application.services.ai.resolve_ai_entities import resolve_ai_entities
from osah.application.services.ai.resolve_employee_from_registry import resolve_employee_from_registry
from osah.application.services.ai.search_employees_by_query import search_employees_by_query
from osah.application.services.initialize_application import initialize_application
from osah.domain.entities.ai_bulk_audience_spec import AiBulkAudienceSpec
from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_entity_resolution_status import AiEntityResolutionStatus
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.services.ai.compiler.compile_ai_command import compile_ai_command
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class UnifiedRegistryGroundingTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary_directory = tempfile.TemporaryDirectory()
        os.environ["OSAH_ENABLE_DEMO_SEED"] = "1"
        application_paths = build_application_paths(Path(self._temporary_directory.name))
        self._context = initialize_application(application_paths)
        self._database_path = self._context.database_path

    def tearDown(self) -> None:
        shut_down_logging()
        self._temporary_directory.cleanup()

    def test_trusted_llm_employee_query_not_overwritten_by_regex(self) -> None:
        draft = AiCommandDraft(
            intent=AiIntentKind.CREATE_PPE_ISSUANCE,
            raw_command="Выдай каску Яценко Андрей сегодняшней датой.",
            source="llm",
            employee_query="Яценко Андрей",
            issue_date="сьогодні",
        )
        compiled = compile_ai_command(draft).draft
        self.assertEqual(compiled.employee_query, "Яценко Андрей")
        self.assertNotIn(". Дата", compiled.employee_query or "")

    def test_ru_andrey_matches_ua_andriy(self) -> None:
        matches = search_employees_by_query(self._database_path, "Яценко Андрей")
        self.assertEqual(len(matches), 1)
        self.assertIn("Андрій", matches[0].full_name)

        dative_matches = search_employees_by_query(self._database_path, "Яценко Андрею")
        self.assertEqual(len(dative_matches), 1)
        self.assertEqual(dative_matches[0].personnel_number, matches[0].personnel_number)

    def test_employee_suggest_on_near_miss(self) -> None:
        resolution = resolve_employee_from_registry(self._database_path, "Яценко Андре")
        if resolution.status == "suggest":
            self.assertGreater(len(resolution.candidates), 0)
            self.assertTrue(any("Яценко" in candidate for candidate in resolution.candidates))
            return

        entity_resolution = resolve_ai_entities(
            self._database_path,
            AiCommandDraft(
                intent=AiIntentKind.QUERY_EMPLOYEE_READINESS,
                raw_command="стан Яценко Андре",
                source="llm",
                employee_query="Яценко Андре",
            ),
        )
        if entity_resolution.status == AiEntityResolutionStatus.NEEDS_CLARIFICATION:
            self.assertIn("Ви мали на увазі", entity_resolution.message or "")
            self.assertGreater(len(entity_resolution.choices), 0)

    def test_cross_field_department_to_position_retry(self) -> None:
        draft = AiCommandDraft(
            intent=AiIntentKind.BULK_CREATE_PPE_ISSUANCE,
            raw_command="выдай всем электромонтеры перчатки",
            source="llm",
            bulk_audience_spec=AiBulkAudienceSpec(department_query="электромонтеры"),
        )
        result = ground_ai_command_draft(self._database_path, draft)
        if not result.ok:
            self.assertIn(result.choice_kind, {"position", "department"})
            if result.choice_kind == "position":
                self.assertGreater(len(result.choices), 0)
                self.assertTrue(
                    "Ви мали на увазі" in (result.message or "")
                    or "кілька варіантів" in (result.message or "")
                )
            return

        grounded_spec = result.draft.bulk_audience_spec
        self.assertIsNotNone(grounded_spec)
        position_query = (grounded_spec.position_query or "").strip().lower()
        department_query = (grounded_spec.department_query or "").strip()
        self.assertTrue(position_query.startswith("електромонтер") or not department_query)

    def test_bulk_position_choice_after_cross_field_retry_resolves(self) -> None:
        draft = AiCommandDraft(
            intent=AiIntentKind.BULK_CREATE_PPE_ISSUANCE,
            raw_command="Выдай всем Электромонтерам по паре защитных рукавиц",
            source="llm",
            bulk_audience_spec=AiBulkAudienceSpec(department_query="Электромонтеры"),
        )
        ambiguous = ground_ai_command_draft(self._database_path, draft)
        self.assertFalse(ambiguous.ok)
        self.assertEqual(ambiguous.choice_kind, "position")

        electrician_choice = next(
            (choice.choice_id for choice in ambiguous.choices if "монтер" in choice.choice_id.lower()),
            ambiguous.choices[0].choice_id,
        )
        updated = apply_grounding_bulk_audience_choice(
            draft,
            electrician_choice,
            choice_kind="position",
        )
        self.assertIsNone(updated.bulk_audience_spec.department_query)
        self.assertEqual(updated.bulk_audience_spec.position_query, electrician_choice)

        result = ground_ai_command_draft(self._database_path, updated)
        self.assertTrue(result.ok)
        self.assertEqual(result.draft.bulk_audience_spec.position_query, electrician_choice)
        self.assertIsNone(result.draft.bulk_audience_spec.department_query)

    def test_compile_preserves_trusted_bulk_audience(self) -> None:
        draft = AiCommandDraft(
            intent=AiIntentKind.BULK_CREATE_PPE_ISSUANCE,
            raw_command="выдай всем в должности электромонтера перчатки",
            source="llm",
            bulk_audience_spec=AiBulkAudienceSpec(position_query="электромонтера"),
        )
        compiled = compile_ai_command(draft).draft
        self.assertEqual(compiled.bulk_audience_spec.position_query, "электромонтера")


if __name__ == "__main__":
    unittest.main()
