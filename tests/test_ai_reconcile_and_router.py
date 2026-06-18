import unittest

from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.services.ai.reconcile_ai_command_draft import reconcile_ai_command_draft
from osah.domain.services.ai.try_match_simple_ai_command import try_match_simple_ai_command


class AiReconcileTests(unittest.TestCase):
    def test_bulk_command_promoted_not_unknown(self) -> None:
        draft = reconcile_ai_command_draft(
            AiCommandDraft(
                intent=AiIntentKind.CREATE_PPE_ISSUANCE,
                raw_command="Додай всім каски",
                source="llm",
            )
        )
        self.assertEqual(draft.intent, AiIntentKind.BULK_CREATE_PPE_ISSUANCE)
        self.assertIsNotNone(draft.clarification_message)

    def test_missing_ppe_with_employee_reroutes_to_readiness(self) -> None:
        draft = reconcile_ai_command_draft(
            AiCommandDraft(
                intent=AiIntentKind.QUERY_MISSING_PPE,
                raw_command="Що потрібно для Білик",
                source="llm",
                employee_query="Білик",
            )
        )
        self.assertEqual(draft.intent, AiIntentKind.QUERY_EMPLOYEE_READINESS)

    def test_close_today_reroutes_from_show_overdue(self) -> None:
        draft = reconcile_ai_command_draft(
            AiCommandDraft(
                intent=AiIntentKind.SHOW_OVERDUE,
                raw_command="Покажи, что нужно закрыть сегодня",
                source="llm",
            )
        )
        self.assertEqual(draft.intent, AiIntentKind.QUERY_DAILY_FOCUS)


class AiRouterV11Tests(unittest.TestCase):
    def test_daily_focus_synonym(self) -> None:
        draft = try_match_simple_ai_command("Дай коротку картину")
        self.assertIsNotNone(draft)
        assert draft is not None
        self.assertEqual(draft.intent, AiIntentKind.QUERY_DAILY_FOCUS)

    def test_overdue_summary_router(self) -> None:
        draft = try_match_simple_ai_command("Покажи критичні проблеми")
        self.assertIsNotNone(draft)
        assert draft is not None
        self.assertEqual(draft.intent, AiIntentKind.QUERY_OVERDUE_SUMMARY)

    def test_missing_ppe_router(self) -> None:
        draft = try_match_simple_ai_command("Кому не видали каску?")
        self.assertIsNotNone(draft)
        assert draft is not None
        self.assertEqual(draft.intent, AiIntentKind.QUERY_MISSING_PPE)

    def test_readiness_router(self) -> None:
        draft = try_match_simple_ai_command("Що потрібно для Білик С.С.?")
        self.assertIsNotNone(draft)
        assert draft is not None
        self.assertEqual(draft.intent, AiIntentKind.QUERY_EMPLOYEE_READINESS)
        self.assertEqual(draft.employee_query, "Білик С.С.")

    def test_port_r_navigation(self) -> None:
        draft = try_match_simple_ai_command("Відкрий PORT-R")
        self.assertIsNotNone(draft)
        assert draft is not None
        self.assertEqual(draft.section_key, "port_r")

    def test_generate_report_router(self) -> None:
        draft = try_match_simple_ai_command("Збери звіт за зміну")
        self.assertIsNotNone(draft)
        assert draft is not None
        self.assertEqual(draft.intent, AiIntentKind.GENERATE_REPORT_TEXT)

    def test_ppe_navigation_router_accepts_russian_ziz(self) -> None:
        draft = try_match_simple_ai_command("Покажи ЗИЗ")
        self.assertIsNotNone(draft)
        assert draft is not None
        self.assertEqual(draft.intent, AiIntentKind.NAVIGATE_SECTION)
        self.assertEqual(draft.section_key, "ppe")

    def test_medical_navigation_router_accepts_russian_medosmotry(self) -> None:
        draft = try_match_simple_ai_command("Покажи медосмотры")
        self.assertIsNotNone(draft)
        assert draft is not None
        self.assertEqual(draft.intent, AiIntentKind.NAVIGATE_SECTION)
        self.assertEqual(draft.section_key, "medical")

    def test_daily_focus_povestka_router(self) -> None:
        draft = try_match_simple_ai_command("Что у нас на повестке дня?")
        self.assertIsNotNone(draft)
        assert draft is not None
        self.assertEqual(draft.intent, AiIntentKind.QUERY_DAILY_FOCUS)

    def test_employees_warning_status_router(self) -> None:
        draft = try_match_simple_ai_command("Покажи работников со статусом Внимание")
        self.assertIsNotNone(draft)
        assert draft is not None
        self.assertEqual(draft.intent, AiIntentKind.QUERY_EMPLOYEES_FILTER)
        self.assertEqual(draft.filter_key, "warning")

    def test_open_trainings_plural_navigates(self) -> None:
        draft = try_match_simple_ai_command("Открой инструктажи")
        self.assertIsNotNone(draft)
        assert draft is not None
        self.assertEqual(draft.intent, AiIntentKind.NAVIGATE_SECTION)
        self.assertEqual(draft.section_key, "trainings")

    def test_unclosed_training_list_query(self) -> None:
        from osah.domain.services.ai.extract_module_status_query_from_command import (
            extract_module_status_query_from_command,
        )

        extracted = extract_module_status_query_from_command(
            "У кого из сотрудников не закрыт инструктаж?"
        )
        self.assertIsNotNone(extracted)
        assert extracted is not None
        self.assertEqual(extracted[0], "trainings")
        self.assertEqual(extracted[1], "warning")


if __name__ == "__main__":
    unittest.main()
