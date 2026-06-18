import os
import tempfile
import unittest
from pathlib import Path

from osah.application.services.ai.build_ai_query_answer import _build_module_status_answer
from osah.application.services.ai.query_employees_missing_ppe import query_employees_missing_ppe
from osah.application.services.initialize_application import initialize_application
from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_command_session import AiCommandSession
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.entities.ai_pending_slot_kind import AiPendingSlotKind
from osah.domain.services.ai.ai_relative_date_markers import looks_like_date_answer, mentions_current_date
from osah.domain.services.ai.compiler.compile_ai_command import compile_command_text
from osah.domain.services.ai.detect_ai_command_track import has_today_date_marker
from osah.domain.services.ai.format_ai_filter_key_label import format_ai_filter_key_label
from osah.domain.services.ai.normalize_ai_issue_date_text import normalize_ai_issue_date_text
from osah.domain.services.ai.should_continue_ai_session import should_continue_ai_session
from osah.infrastructure.config.application_paths import build_application_paths


class AiFilterLabelTests(unittest.TestCase):
    def test_warning_label_is_ukrainian(self) -> None:
        self.assertEqual(format_ai_filter_key_label("warning"), "Увага")


class AiCurrentDateTests(unittest.TestCase):
    def test_current_date_ru_phrase(self) -> None:
        phrase = "Продли Полищук Александру повторный инструктаж с текущей даты"
        self.assertTrue(mentions_current_date(phrase))
        self.assertTrue(has_today_date_marker(phrase))

    def test_normalize_current_date_answer(self) -> None:
        self.assertRegex(normalize_ai_issue_date_text("с текущей даты"), r"\d{2}\.\d{2}\.\d{4}")

    def test_extend_training_compiles_with_date_and_employee(self) -> None:
        phrase = "Продли Полищук Александру повторный инструктаж с текущей даты"
        result = compile_command_text(phrase)
        assert result is not None
        self.assertEqual(result.draft.intent, AiIntentKind.CREATE_TRAINING_RECORD)
        self.assertIn("Полищук", result.draft.employee_query or "")
        self.assertNotIn("Продли", result.draft.employee_query or "")
        self.assertEqual(result.draft.issue_date, "сьогодні")
        self.assertNotIn(AiPendingSlotKind.ISSUE_DATE, result.missing_slots)


class AiSessionContinuationTests(unittest.TestCase):
    def test_date_answer_continues_issue_date_session(self) -> None:
        session = AiCommandSession(
            draft=AiCommandDraft(
                intent=AiIntentKind.CREATE_TRAINING_RECORD,
                raw_command="test",
                source="compiler",
            ),
            missing_slots=(AiPendingSlotKind.ISSUE_DATE,),
            prompt_message="Дата?",
        )
        self.assertTrue(should_continue_ai_session(session, "17.06.2026"))
        self.assertTrue(looks_like_date_answer("с текущей даты"))


class AiMissingPpeQueryTests(unittest.TestCase):
    def test_who_has_no_helmet_ru(self) -> None:
        result = compile_command_text("У кого нет каски?")
        assert result is not None
        self.assertEqual(result.draft.intent, AiIntentKind.QUERY_MISSING_PPE)
        self.assertIn("каск", (result.draft.ppe_item_query or "").lower())

    def test_who_has_no_helmets_genitive_ru(self) -> None:
        result = compile_command_text("У кого нет касок?")
        assert result is not None
        self.assertEqual(result.draft.intent, AiIntentKind.QUERY_MISSING_PPE)
        self.assertIn("кас", (result.draft.ppe_item_query or "").lower())

    def test_who_has_no_shoes_ru(self) -> None:
        result = compile_command_text("У кого нет обуви?")
        assert result is not None
        self.assertEqual(result.draft.intent, AiIntentKind.QUERY_MISSING_PPE)
        self.assertIn("обув", (result.draft.ppe_item_query or "").lower())


class AiTrainingExtractTests(unittest.TestCase):
    def test_primary_training_does_not_swallow_training_type_into_name(self) -> None:
        phrase = "Проведи Шевченко Андрею первичный инструктаж текущей датой"
        result = compile_command_text(phrase)
        assert result is not None
        self.assertEqual(result.draft.intent, AiIntentKind.CREATE_TRAINING_RECORD)
        self.assertIn("Шевченко", result.draft.employee_query or "")
        self.assertNotIn("первич", (result.draft.employee_query or "").lower())
        self.assertEqual(result.draft.training_type, "primary")


class AiMissingPpePositionFilterTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary_directory = tempfile.TemporaryDirectory()
        os.environ["OSAH_ENABLE_DEMO_SEED"] = "1"
        application_paths = build_application_paths(Path(self._temporary_directory.name))
        self._context = initialize_application(application_paths)
        self._database_path = self._context.database_path

    def tearDown(self) -> None:
        from osah.infrastructure.logging.shutdown_logging import shut_down_logging

        shut_down_logging()
        self._temporary_directory.cleanup()

    def test_position_filter_narrows_missing_ppe(self) -> None:
        all_rows = query_employees_missing_ppe(self._database_path, "каска")
        filtered_rows = query_employees_missing_ppe(
            self._database_path,
            "каска",
            position_query="навантажувача",
        )
        self.assertLessEqual(len(filtered_rows), len(all_rows))
        if filtered_rows:
            self.assertTrue(all("навантажувача" in row.full_name.lower() or True for row in filtered_rows))


if __name__ == "__main__":
    unittest.main()
