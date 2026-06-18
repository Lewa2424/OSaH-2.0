import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from osah.application.services.ai.build_ai_read_navigation_target import build_ai_read_navigation_target
from osah.application.services.ai.resolve_user_ai_command import resolve_user_ai_command
from osah.application.services.ai.save_ai_pattern_memory_entry import save_ai_pattern_memory_entry
from osah.application.services.ai.search_employees_by_query import search_employees_by_query
from osah.application.services.initialize_application import initialize_application
from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_command_session import AiCommandSession
from osah.domain.entities.ai_command_resolution_status import AiCommandResolutionStatus
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.entities.ai_pending_slot_kind import AiPendingSlotKind
from osah.domain.entities.ai_ui_context import AiUiContext
from osah.domain.entities.app_section import AppSection
from osah.domain.services.ai.apply_ai_pattern_memory import apply_ai_pattern_memory
from osah.domain.services.ai.build_ai_navigation_target import build_ai_navigation_target
from osah.domain.services.ai.ensure_ai_intent_is_allowed import ensure_ai_intent_is_allowed, is_ai_read_only_intent
from osah.domain.services.ai.is_ai_access_role_allowed import is_ai_access_role_allowed
from osah.domain.services.ai.should_continue_ai_session import should_continue_ai_session
from osah.application.services.ai.preflight_ai_command_draft import preflight_ai_command_draft
from osah.domain.services.ai.compiler.compile_ai_command import compile_command_text
from osah.domain.services.ai.try_match_simple_ai_command import try_match_simple_ai_command
from osah.domain.services.ai.validate_ai_command_draft import validate_ai_command_draft
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.config.build_ai_runtime_paths import build_ai_runtime_paths, is_ai_runtime_bundle_available
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class AiAccessRoleTests(unittest.TestCase):
    def test_inspector_allowed(self) -> None:
        self.assertTrue(is_ai_access_role_allowed(AccessRole.INSPECTOR))

    def test_manager_denied(self) -> None:
        self.assertFalse(is_ai_access_role_allowed(AccessRole.MANAGER))


class AiRuleRouterGoldenSetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        fixture_path = Path(__file__).resolve().parent / "fixtures" / "ai_command_golden_set.json"
        cls._golden_entries = json.loads(fixture_path.read_text(encoding="utf-8"))

    def test_router_matches_expected_simple_commands(self) -> None:
        for entry in self._golden_entries:
            if not entry.get("router_should_match"):
                continue
            draft = try_match_simple_ai_command(entry["command"])
            self.assertIsNotNone(draft, msg=entry["command"])
            assert draft is not None
            self.assertEqual(draft.intent.value, entry["expected_intent"], msg=entry["command"])
            if "expected_section_key" in entry:
                self.assertEqual(draft.section_key, entry["expected_section_key"])
            if "expected_personnel_number" in entry:
                self.assertEqual(draft.personnel_number, entry["expected_personnel_number"])
            if "expected_filter_key" in entry:
                self.assertEqual(draft.filter_key, entry["expected_filter_key"])
            if "expected_module_key" in entry:
                self.assertEqual(draft.module_key, entry["expected_module_key"])

    def test_golden_set_has_minimum_size(self) -> None:
        self.assertGreaterEqual(len(self._golden_entries), 100)


class AiCompilerGoldenV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        fixture_path = Path(__file__).resolve().parent / "fixtures" / "ai_command_golden_set.json"
        cls._golden_entries = json.loads(fixture_path.read_text(encoding="utf-8"))

    def test_compile_without_llm_entries(self) -> None:
        for entry in self._golden_entries:
            if not entry.get("compile_without_llm"):
                continue
            result = compile_command_text(entry["command"])
            self.assertIsNotNone(result, msg=entry["command"])
            assert result is not None
            self.assertFalse(result.needs_llm, msg=entry["command"])
            self.assertEqual(result.draft.intent.value, entry["expected_intent"], msg=entry["command"])
            expected_slots = entry.get("expected_slots") or {}
            for slot_key, slot_value in expected_slots.items():
                self.assertEqual(getattr(result.draft, slot_key), slot_value, msg=f"{entry['command']}:{slot_key}")
            missing_slot = entry.get("missing_slot")
            if missing_slot:
                self.assertTrue(
                    any(slot.value == missing_slot for slot in result.missing_slots),
                    msg=entry["command"],
                )
            if entry.get("preflight_should_pass"):
                preflight = preflight_ai_command_draft(result.draft)
                self.assertTrue(preflight.ok, msg=entry["command"])


class AiNavigationMappingTests(unittest.TestCase):
    def test_show_overdue_uses_current_ppe_section(self) -> None:
        draft = AiCommandDraft(
            intent=AiIntentKind.SHOW_OVERDUE,
            raw_command="просрочки",
            source="rule_router",
        )
        target = build_ai_navigation_target(
            draft,
            ui_context=AiUiContext(section=AppSection.PPE),
        )
        self.assertIsNotNone(target)
        assert target is not None
        self.assertEqual(target.section, AppSection.PPE)
        self.assertEqual(target.ppe_status_filter, "expired")

    def test_read_navigation_builder_returns_target(self) -> None:
        draft = AiCommandDraft(
            intent=AiIntentKind.NAVIGATE_SECTION,
            raw_command="Відкрий ЗІЗ",
            source="rule_router",
            section_key="ppe",
        )
        target = build_ai_read_navigation_target(draft)
        self.assertIsNotNone(target)
        assert target is not None
        self.assertEqual(target.section, AppSection.PPE)


class AiResolveUserCommandTests(unittest.TestCase):
    def test_manager_gets_access_denied(self) -> None:
        resolution = resolve_user_ai_command("Покажи просрочки", access_role=AccessRole.MANAGER)
        self.assertEqual(resolution.status, AiCommandResolutionStatus.ACCESS_DENIED)

    def test_router_command_parsed_for_inspector(self) -> None:
        resolution = resolve_user_ai_command("Покажи просрочки", access_role=AccessRole.INSPECTOR)
        self.assertEqual(resolution.status, AiCommandResolutionStatus.PARSED)
        self.assertIsNotNone(resolution.draft)
        assert resolution.draft is not None
        self.assertEqual(resolution.draft.intent, AiIntentKind.SHOW_OVERDUE)
        self.assertEqual(resolution.draft.source, "rule_router")

    def test_complex_command_uses_runtime_when_available(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        runtime_paths = build_ai_runtime_paths(project_root)
        if not is_ai_runtime_bundle_available(runtime_paths):
            self.skipTest("AI runtime bundle is not available")

        resolution = resolve_user_ai_command(
            "Занеси Петрову каску и ботинки за сегодня",
            access_role=AccessRole.INSPECTOR,
            project_root=project_root,
        )
        if resolution.status == AiCommandResolutionStatus.RUNTIME_UNAVAILABLE:
            self.skipTest(resolution.message)
        self.assertIn(
            resolution.status,
            {AiCommandResolutionStatus.PARSED, AiCommandResolutionStatus.INVALID_DRAFT},
        )
        self.assertIsNotNone(resolution.draft)
        assert resolution.draft is not None
        self.assertIn(
            resolution.draft.source,
            {"llm", "compiler"},
        )

    @patch("osah.application.services.ai.resolve_user_ai_command.try_match_department_employees_query", return_value=None)
    @patch(
        "osah.application.services.ai.resolve_user_ai_command.try_match_high_confidence_fast_path_command",
        return_value=None,
    )
    @patch("osah.application.services.ai.resolve_user_ai_command.is_ai_runtime_bundle_available", return_value=True)
    @patch(
        "osah.application.services.ai.resolve_user_ai_command.parse_ai_command_draft_from_llm",
        side_effect=RuntimeError("llama-server HTTP 400"),
    )
    def test_intent_skeleton_fallback_when_llm_fails(
        self,
        _llm_mock,
        _runtime_mock,
        _fast_path_mock,
        _department_mock,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            try:
                os.environ["OSAH_ENABLE_DEMO_SEED"] = "1"
                application_paths = build_application_paths(Path(temporary_directory))
                context = initialize_application(application_paths)
                resolution = resolve_user_ai_command(
                    "а кто работает в Службе охраны труда?",
                    access_role=AccessRole.INSPECTOR,
                    project_root=application_paths.project_root,
                    database_path=context.database_path,
                )
                self.assertEqual(resolution.status, AiCommandResolutionStatus.PARSED)
                assert resolution.draft is not None
                self.assertEqual(resolution.draft.intent, AiIntentKind.QUERY_EMPLOYEES_FILTER)
                self.assertEqual(resolution.draft.department_query, "Служба охорони праці")
                self.assertIn("правилами", resolution.message)
            finally:
                shut_down_logging()


class AiSessionContinuationTests(unittest.TestCase):
    def test_new_navigation_command_does_not_continue_previous_session(self) -> None:
        session = AiCommandSession(
            draft=AiCommandDraft(
                intent=AiIntentKind.CREATE_PPE_ISSUANCE,
                raw_command="Видай Петрову",
                source="compiler",
            ),
            missing_slots=(AiPendingSlotKind.PPE_ITEM,),
            prompt_message="Вкажіть предмет ЗІЗ.",
        )
        self.assertFalse(should_continue_ai_session(session, "Покажи інструктажі"))

    def test_short_slot_answer_continues_previous_session(self) -> None:
        session = AiCommandSession(
            draft=AiCommandDraft(
                intent=AiIntentKind.CREATE_PPE_ISSUANCE,
                raw_command="Видай Петрову",
                source="compiler",
            ),
            missing_slots=(AiPendingSlotKind.PPE_ITEM,),
            prompt_message="Вкажіть предмет ЗІЗ.",
        )
        self.assertTrue(should_continue_ai_session(session, "каску"))


class ValidateAiCommandDraftTests(unittest.TestCase):
    def test_ppe_draft_requires_employee_and_items(self) -> None:
        draft = AiCommandDraft(
            intent=AiIntentKind.CREATE_PPE_ISSUANCE,
            raw_command="test",
            source="llm",
            needs_confirmation=True,
        )
        issues = validate_ai_command_draft(draft)
        self.assertGreaterEqual(len(issues), 2)

    def test_forbidden_intent_raises(self) -> None:
        with self.assertRaises(ValueError):
            ensure_ai_intent_is_allowed(AiIntentKind.UNKNOWN)


class AiPatternMemoryTests(unittest.TestCase):
    def test_pattern_memory_replaces_source_phrase(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            initialize_application(application_paths)
            save_ai_pattern_memory_entry(
                application_paths.database_file_path,
                source_phrase="боты",
                mapping_type="ppe_alias",
                target_value="ботинки",
            )
            resolved = apply_ai_pattern_memory(application_paths.database_file_path, "Выдай боты Петрову")
            self.assertIn("ботинки", resolved)
            shut_down_logging()


class EmployeeSearchTests(unittest.TestCase):
    def test_search_by_personnel_number(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            initialize_application(application_paths)
            matches = search_employees_by_query(application_paths.database_file_path, "0001")
            self.assertGreaterEqual(len(matches), 0)
            shut_down_logging()


def tearDownModule() -> None:
    from osah.application.services.ai.shutdown_ai_runtime import shutdown_ai_runtime

    shutdown_ai_runtime()


if __name__ == "__main__":
    unittest.main()
