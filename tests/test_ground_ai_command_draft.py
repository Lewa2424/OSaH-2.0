import os
import tempfile
import unittest
from pathlib import Path

from osah.application.services.ai.apply_grounding_entity_choice import apply_grounding_entity_choice
from osah.application.services.ai.ground_ai_command_draft import ground_ai_command_draft
from osah.application.services.ai.resolve_department_from_registry import resolve_department_from_registry
from osah.application.services.ai.resolve_position_from_registry import resolve_position_from_registry
from osah.application.services.ai.resolve_user_ai_command import resolve_user_ai_command
from osah.application.services.initialize_application import initialize_application
from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_command_resolution_status import AiCommandResolutionStatus
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.services.ai.match_position_name_query import position_name_matches_query
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class GroundAiCommandDraftTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary_directory = tempfile.TemporaryDirectory()
        os.environ["OSAH_ENABLE_DEMO_SEED"] = "1"
        application_paths = build_application_paths(Path(self._temporary_directory.name))
        self._application_paths = application_paths
        self._context = initialize_application(application_paths)
        self._database_path = self._context.database_path

    def tearDown(self) -> None:
        shut_down_logging()
        self._temporary_directory.cleanup()

    def test_department_resolves_single_match(self) -> None:
        resolution = resolve_department_from_registry(self._database_path, "Лаборатория")
        self.assertEqual(resolution.status, "resolved")
        self.assertEqual(resolution.canonical_name, "Лабораторія контролю якості")

    def test_department_resolves_russian_variant(self) -> None:
        resolution = resolve_department_from_registry(self._database_path, "Службе охраны труда")
        self.assertEqual(resolution.status, "resolved")
        self.assertEqual(resolution.canonical_name, "Служба охорони праці")

    def test_position_resolves_loader_driver(self) -> None:
        resolution = resolve_position_from_registry(self._database_path, "навантажувача")
        self.assertEqual(resolution.status, "resolved")
        self.assertEqual(resolution.canonical_name, "Водій навантажувача")

    def test_ground_department_draft(self) -> None:
        draft = AiCommandDraft(
            intent=AiIntentKind.QUERY_EMPLOYEES_FILTER,
            raw_command="test",
            source="test",
            filter_key="department",
            department_query="Лаборатория",
        )
        result = ground_ai_command_draft(self._database_path, draft)
        self.assertTrue(result.ok)
        self.assertEqual(result.draft.department_query, "Лабораторія контролю якості")
        self.assertIsNone(result.draft.employee_query)

    def test_ambiguous_department_returns_choices(self) -> None:
        resolution = resolve_department_from_registry(self._database_path, "служб")
        self.assertEqual(resolution.status, "ambiguous")
        draft = AiCommandDraft(
            intent=AiIntentKind.QUERY_EMPLOYEES_FILTER,
            raw_command="test",
            source="test",
            filter_key="department",
            department_query="служб",
        )
        result = ground_ai_command_draft(self._database_path, draft)
        self.assertFalse(result.ok)
        self.assertEqual(result.choice_kind, "department")
        self.assertGreater(len(result.choices), 1)

    def test_apply_grounding_department_choice_resolves(self) -> None:
        draft = AiCommandDraft(
            intent=AiIntentKind.QUERY_EMPLOYEES_FILTER,
            raw_command="test",
            source="test",
            filter_key="department",
            department_query="служб",
        )
        ambiguous = ground_ai_command_draft(self._database_path, draft)
        self.assertFalse(ambiguous.ok)
        chosen = ambiguous.choices[0].choice_id
        updated = apply_grounding_entity_choice(draft, chosen, choice_kind="department")
        result = ground_ai_command_draft(self._database_path, updated)
        self.assertTrue(result.ok)
        self.assertEqual(result.draft.department_query, chosen)

    def test_employee_ambiguous_grounding_returns_choices_without_crash(self) -> None:
        draft = AiCommandDraft(
            intent=AiIntentKind.CREATE_TRAINING_RECORD,
            raw_command="Добавь для Демченко Натальи ограничение по работе на высоте",
            source="llm",
            employee_query="Демченко",
        )
        result = ground_ai_command_draft(self._database_path, draft)
        if result.ok:
            self.assertTrue((result.draft.personnel_number or "").strip() or (result.draft.employee_query or "").strip())
            return
        self.assertEqual(result.choice_kind, "employee")
        self.assertGreater(len(result.choices), 0)

    def test_resolve_ambiguous_department_returns_entity_choices(self) -> None:
        resolution = resolve_user_ai_command(
            "Кто работает в подразделении служб?",
            access_role=AccessRole.INSPECTOR,
            project_root=self._application_paths.project_root,
            database_path=self._database_path,
        )
        self.assertEqual(resolution.status, AiCommandResolutionStatus.NEEDS_CLARIFICATION)
        self.assertGreater(len(resolution.entity_choices), 1)
        self.assertEqual(resolution.pending_grounding_choice_kind, "department")

    def test_position_token_match(self) -> None:
        self.assertTrue(position_name_matches_query("Водій навантажувача", "навантажувача"))


if __name__ == "__main__":
    unittest.main()
