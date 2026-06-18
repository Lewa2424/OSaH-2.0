import os
import tempfile
import unittest
from pathlib import Path

from osah.application.services.ai.resolve_user_ai_command import resolve_user_ai_command
from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.ai_command_resolution_status import AiCommandResolutionStatus
from osah.domain.entities.ai_conversation_context import AiConversationContext
from osah.domain.entities.ai_conversation_pending_kind import AiConversationPendingKind
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.services.ai.matches_audience_anaphora import matches_audience_anaphora
from osah.domain.services.ai.matches_department_employees_query import extract_department_employees_query
from osah.domain.services.ai.matches_department_list_follow_up import matches_department_list_follow_up
from osah.domain.services.ai.try_build_draft_from_conversation_context import (
    try_build_draft_from_conversation_context,
)
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class ConversationMatcherTests(unittest.TestCase):
    def test_audience_anaphora_ru(self) -> None:
        self.assertTrue(matches_audience_anaphora("выдай им каски сегодняшней датой"))

    def test_department_query_extract(self) -> None:
        self.assertEqual(
            extract_department_employees_query("Кто у нас работает в подразделении Лаборатория?"),
            "Лаборатория",
        )
        self.assertEqual(
            extract_department_employees_query("а кто работает в Службе охраны труда?"),
            "Службе охраны труда",
        )

    def test_department_list_follow_up(self) -> None:
        self.assertTrue(matches_department_list_follow_up("Список сотрудников"))


class ConversationDraftTests(unittest.TestCase):
    def test_bulk_ppe_from_missing_ppe_context(self) -> None:
        context = AiConversationContext(
            resolved_personnel_numbers=("0001", "0002"),
            ppe_item_query="каска",
            source_intent=AiIntentKind.QUERY_MISSING_PPE.value,
        )
        draft = try_build_draft_from_conversation_context(
            "выдай им каски сегодняшней датой",
            context,
        )
        self.assertIsNotNone(draft)
        assert draft is not None
        self.assertEqual(draft.intent, AiIntentKind.BULK_CREATE_PPE_ISSUANCE)
        self.assertEqual(draft.bulk_audience_spec.resolved_personnel_numbers, ("0001", "0002"))

    def test_department_list_from_pending_context(self) -> None:
        context = AiConversationContext(
            department_query="Лабораторія контролю якості",
            pending_kind=AiConversationPendingKind.DEPARTMENT_EMPLOYEES,
        )
        draft = try_build_draft_from_conversation_context("список сотрудников", context)
        self.assertIsNotNone(draft)
        assert draft is not None
        self.assertEqual(draft.intent, AiIntentKind.QUERY_EMPLOYEES_FILTER)
        self.assertEqual(draft.filter_key, "department")


class ConversationResolveTests(unittest.TestCase):
    def test_department_question_returns_employee_list(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            try:
                os.environ["OSAH_ENABLE_DEMO_SEED"] = "1"
                application_paths = build_application_paths(Path(temporary_directory))
                from osah.application.services.initialize_application import initialize_application

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
                self.assertEqual(resolution.draft.department_query, "Лабораторія контролю якості")
            finally:
                shut_down_logging()

    def test_anaphora_bulk_ppe_without_llm(self) -> None:
        context = AiConversationContext(
            resolved_personnel_numbers=("0001", "0002"),
            ppe_item_query="каска",
            source_intent=AiIntentKind.QUERY_MISSING_PPE.value,
        )
        resolution = resolve_user_ai_command(
            "выдай им каски сегодняшней датой",
            access_role=AccessRole.INSPECTOR,
            conversation_context=context,
        )
        self.assertEqual(resolution.status, AiCommandResolutionStatus.PARSED)
        assert resolution.draft is not None
        self.assertEqual(resolution.draft.intent, AiIntentKind.BULK_CREATE_PPE_ISSUANCE)
        self.assertEqual(resolution.draft.bulk_audience_spec.resolved_personnel_numbers, ("0001", "0002"))

    def test_department_list_follow_up_without_llm(self) -> None:
        context = AiConversationContext(
            department_query="Лабораторія контролю якості",
            pending_kind=AiConversationPendingKind.DEPARTMENT_EMPLOYEES,
        )
        resolution = resolve_user_ai_command(
            "список сотрудников",
            access_role=AccessRole.INSPECTOR,
            conversation_context=context,
        )
        self.assertEqual(resolution.status, AiCommandResolutionStatus.PARSED)
        assert resolution.draft is not None
        self.assertEqual(resolution.draft.intent, AiIntentKind.QUERY_EMPLOYEES_FILTER)
        self.assertEqual(resolution.draft.filter_key, "department")


if __name__ == "__main__":
    unittest.main()
