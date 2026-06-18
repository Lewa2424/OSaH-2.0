import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from osah.application.services.ai.resolve_user_ai_command import resolve_user_ai_command
from osah.application.services.initialize_application import initialize_application
from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.ai_bulk_audience_spec import AiBulkAudienceSpec
from osah.domain.entities.ai_command_resolution_status import AiCommandResolutionStatus
from osah.domain.entities.ai_conversation_pending_kind import AiConversationPendingKind
from osah.domain.entities.ai_dialogue_state import AiDialogueState
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.services.ai.extract_employee_query_from_command import extract_employee_query_from_command
from osah.domain.services.ai.extract_employee_queries_from_command import extract_employee_queries_from_command
from osah.application.services.ai.search_employees_by_query import search_employees_by_query
from osah.domain.services.ai.resolve_audience_subset_from_command import resolve_audience_subset_from_command
from osah.domain.services.ai.should_apply_ai_dialogue_state import should_apply_ai_dialogue_state
from osah.domain.services.ai.try_build_draft_from_dialogue_state import try_build_draft_from_dialogue_state
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class DialogueAudienceExtractTests(unittest.TestCase):
    def test_employee_role_prefix_is_stripped(self) -> None:
        self.assertEqual(
            extract_employee_query_from_command("выдай каску сотруднику Лысенко Ирине"),
            "Лысенко Ирине",
        )

    def test_split_multiple_names(self) -> None:
        self.assertEqual(
            extract_employee_queries_from_command("выдай каски Лысенко и Петрову"),
            ("Лысенко", "Петрову"),
        )


class DialogueAudienceSubsetTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary_directory = tempfile.TemporaryDirectory()
        os.environ["OSAH_ENABLE_DEMO_SEED"] = "1"
        application_paths = build_application_paths(Path(self._temporary_directory.name))
        self._context = initialize_application(application_paths)
        self._database_path = self._context.database_path
        employees = search_employees_by_query(self._database_path, "Лысенко")
        if len(employees) < 1:
            employees = search_employees_by_query(self._database_path, "а")
        audience_numbers = tuple(employee.personnel_number for employee in employees[:6])
        audience_labels = tuple(employee.full_name for employee in employees[:6])
        if not audience_numbers:
            audience_numbers = ("0001", "0002", "0003")
            audience_labels = ("Тест 1", "Тест 2", "Тест 3")
        self._state = AiDialogueState(
            audience_personnel_numbers=audience_numbers,
            audience_labels=audience_labels,
            ppe_item_query="каска",
            source_intent=AiIntentKind.QUERY_MISSING_PPE.value,
        )
        self._primary_name = employees[0].full_name.split()[0] if employees else "Тест"

    def tearDown(self) -> None:
        shut_down_logging()
        self._temporary_directory.cleanup()

    def test_anaphora_returns_all_six(self) -> None:
        draft = try_build_draft_from_dialogue_state(
            "выдай им каски сегодняшней датой",
            self._state,
            database_path=self._database_path,
        )
        self.assertIsNotNone(draft)
        assert draft is not None
        self.assertEqual(draft.intent, AiIntentKind.BULK_CREATE_PPE_ISSUANCE)
        self.assertEqual(
            len(draft.bulk_audience_spec.resolved_personnel_numbers),
            len(self._state.audience_personnel_numbers),
        )

    def test_named_subset_from_audience(self) -> None:
        subset = resolve_audience_subset_from_command(
            self._database_path,
            f"выдай каски {self._primary_name}",
            self._state,
        )
        self.assertIsNotNone(subset)
        assert subset is not None
        self.assertGreaterEqual(len(subset.personnel_numbers), 1)

    def test_independent_command_clears_dialogue_application(self) -> None:
        self.assertFalse(
            should_apply_ai_dialogue_state(self._state, "Покажи ЗІЗ"),
        )
        self.assertTrue(
            should_apply_ai_dialogue_state(self._state, "выдай каску Лысенко"),
        )

    def test_named_subset_bulk_ppe_compiles_items(self) -> None:
        state = AiDialogueState(
            audience_personnel_numbers=("0040", "0014"),
            audience_labels=("Коваль Роман Сергійович", "Савченко Тетяна Петрович"),
            ppe_item_query="каски",
            source_intent=AiIntentKind.QUERY_MISSING_PPE.value,
        )
        draft = try_build_draft_from_dialogue_state(
            "Выдай каски Коваль Р.С. и Савченко Т.П. сегодняшней датой",
            state,
            database_path=self._database_path,
        )
        self.assertIsNotNone(draft)
        assert draft is not None
        from osah.domain.services.ai.compiler.compile_ai_command import compile_ai_command

        compiled = compile_ai_command(draft)
        assert compiled.draft.bulk_audience_spec is not None
        self.assertEqual(
            compiled.draft.bulk_audience_spec.resolved_personnel_numbers,
            ("0040", "0014"),
        )
        self.assertTrue(compiled.draft.items)
        self.assertIsNone(compiled.draft.employee_query)


class DialogueAudienceResolveTests(unittest.TestCase):
    def test_anaphora_bulk_without_llm(self) -> None:
        state = AiDialogueState(
            audience_personnel_numbers=("0001", "0002"),
            ppe_item_query="каска",
            source_intent=AiIntentKind.QUERY_MISSING_PPE.value,
        )
        resolution = resolve_user_ai_command(
            "выдай им каски сегодняшней датой",
            access_role=AccessRole.INSPECTOR,
            dialogue_state=state,
        )
        self.assertEqual(resolution.status, AiCommandResolutionStatus.PARSED)
        assert resolution.draft is not None
        self.assertEqual(resolution.draft.intent, AiIntentKind.BULK_CREATE_PPE_ISSUANCE)

    def test_department_question_returns_employee_list(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            try:
                os.environ["OSAH_ENABLE_DEMO_SEED"] = "1"
                application_paths = build_application_paths(Path(temporary_directory))
                context = initialize_application(application_paths)
                resolution = resolve_user_ai_command(
                    "Кто у нас работает в подразделении Лаборатория?",
                    access_role=AccessRole.INSPECTOR,
                    project_root=application_paths.project_root,
                    database_path=context.database_path,
                )
                self.assertEqual(resolution.status, AiCommandResolutionStatus.PARSED)
                assert resolution.draft is not None
                self.assertEqual(resolution.draft.intent, AiIntentKind.QUERY_EMPLOYEES_FILTER)
                self.assertEqual(resolution.draft.filter_key, "department")
                self.assertEqual(resolution.draft.department_query, "Лабораторія контролю якості")
            finally:
                shut_down_logging()

    def test_safety_service_department_without_llm(self) -> None:
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
                self.assertEqual(resolution.draft.department_query, "Служба охорони праці")
            finally:
                shut_down_logging()

    @patch("osah.application.services.ai.resolve_user_ai_command.is_ai_runtime_bundle_available", return_value=False)
    def test_fast_path_missing_ppe_without_llm(self, _runtime_mock) -> None:
        resolution = resolve_user_ai_command(
            "У кого нет каски?",
            access_role=AccessRole.INSPECTOR,
        )
        self.assertEqual(resolution.status, AiCommandResolutionStatus.PARSED)
        assert resolution.draft is not None
        self.assertEqual(resolution.draft.intent, AiIntentKind.QUERY_MISSING_PPE)


if __name__ == "__main__":
    unittest.main()
