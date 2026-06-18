import unittest

from osah.application.services.ai.preflight_ai_command_draft import preflight_ai_command_draft
from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_command_session import AiCommandSession
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.entities.ai_pending_slot_kind import AiPendingSlotKind
from osah.domain.services.ai.compiler.compile_ai_command import compile_ai_command, compile_command_text
from osah.domain.services.ai.compiler.fill_ai_command_session import fill_ai_command_session
from osah.domain.services.ai.validate_ai_command_draft import validate_ai_command_draft


class CompileModuleStatusTests(unittest.TestCase):
    def test_module_status_from_ru_phrase(self) -> None:
        result = compile_command_text("У кого в инструктажах статус Внимание?")
        self.assertIsNotNone(result)
        assert result is not None
        self.assertFalse(result.needs_llm)
        self.assertEqual(result.draft.intent, AiIntentKind.QUERY_MODULE_STATUS)
        self.assertEqual(result.draft.module_key, "trainings")
        self.assertEqual(result.draft.filter_key, "warning")


class CompileBulkTests(unittest.TestCase):
    def test_department_bulk_ppe(self) -> None:
        command = (
            "выдай работникам подразделения Ремонтна служба "
            "дополнительно по паре перчаток сегодняшней датой"
        )
        result = compile_ai_command(
            AiCommandDraft(
                intent=AiIntentKind.CREATE_PPE_ISSUANCE,
                raw_command=command,
                source="llm",
                employee_query="Ремонтна служба",
                issue_date="сьогодні",
            )
        )
        self.assertEqual(result.draft.intent, AiIntentKind.BULK_CREATE_PPE_ISSUANCE)
        self.assertIsNotNone(result.draft.bulk_audience_spec)
        assert result.draft.bulk_audience_spec is not None
        self.assertEqual(result.draft.bulk_audience_spec.department_query, "Ремонтна служба")


class CompileTrainingTests(unittest.TestCase):
    def test_koval_repeated_with_relative_period(self) -> None:
        command = "Занеси Коваль Роману повторный инструктаж на 3 месяца с текущей даты"
        result = compile_command_text(command)
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.draft.intent, AiIntentKind.CREATE_TRAINING_RECORD)
        self.assertIn("Коваль", result.draft.employee_query or "")
        self.assertEqual(result.draft.training_type, "repeated")
        self.assertTrue(result.draft.use_manual_next_control_date)
        self.assertIsNotNone(result.draft.next_control_date)

    def test_missing_work_risk_for_repeated(self) -> None:
        draft = AiCommandDraft(
            intent=AiIntentKind.CREATE_TRAINING_RECORD,
            raw_command="Занеси Коваль Роману повторный инструктаж сегодня",
            source="compiler",
            employee_query="Коваль Роман",
            issue_date="сьогодні",
            training_type="repeated",
        )
        result = compile_ai_command(draft)
        self.assertIn(AiPendingSlotKind.WORK_RISK_CATEGORY, result.missing_slots)


class SessionFillTests(unittest.TestCase):
    def test_work_risk_fill_not_section_problems(self) -> None:
        session = AiCommandSession(
            draft=AiCommandDraft(
                intent=AiIntentKind.CREATE_TRAINING_RECORD,
                raw_command="Занеси Коваль Роману повторный инструктаж сегодня",
                source="compiler",
                employee_query="Коваль Роман",
                issue_date="сьогодні",
                training_type="repeated",
            ),
            missing_slots=(AiPendingSlotKind.WORK_RISK_CATEGORY,),
            prompt_message="Категорія?",
        )
        result = fill_ai_command_session(session, "Категория - опасные работы")
        self.assertEqual(result.draft.intent, AiIntentKind.CREATE_TRAINING_RECORD)
        self.assertEqual(result.draft.work_risk_category, "high_risk")
        self.assertNotEqual(result.draft.intent, AiIntentKind.QUERY_SECTION_PROBLEMS)


class PreflightTrainingTests(unittest.TestCase):
    def test_preflight_computes_next_control(self) -> None:
        draft = AiCommandDraft(
            intent=AiIntentKind.CREATE_TRAINING_RECORD,
            raw_command="test",
            source="compiler",
            issue_date="сьогодні",
            training_type="repeated",
            work_risk_category="high_risk",
        )
        preflight = preflight_ai_command_draft(draft)
        self.assertTrue(preflight.ok)
        self.assertTrue(preflight.enriched_draft.next_control_date)


class CompileRegressionTests(unittest.TestCase):
    def test_readiness_not_overridden(self) -> None:
        result = compile_ai_command(
            AiCommandDraft(
                intent=AiIntentKind.QUERY_MISSING_PPE,
                raw_command="Що потрібно для Білик",
                source="llm",
                employee_query="Білик",
            )
        )
        self.assertEqual(result.draft.intent, AiIntentKind.QUERY_EMPLOYEE_READINESS)

    def test_section_problems_stays_list(self) -> None:
        result = compile_ai_command(
            AiCommandDraft(
                intent=AiIntentKind.QUERY_OVERDUE_SUMMARY,
                raw_command="які зараз є проблемні розділи?",
                source="llm",
            )
        )
        self.assertEqual(result.draft.intent, AiIntentKind.QUERY_SECTION_PROBLEMS)

    def test_module_status_validates(self) -> None:
        result = compile_command_text("У кого в инструктажах статус Внимание?")
        assert result is not None
        self.assertEqual(validate_ai_command_draft(result.draft), [])


class CompileRecognitionFixTests(unittest.TestCase):
    def test_nav_ru_open_trainings(self) -> None:
        result = compile_command_text("Открой инструктажи")
        assert result is not None
        self.assertEqual(result.draft.intent, AiIntentKind.NAVIGATE_SECTION)
        self.assertEqual(result.draft.section_key, "trainings")

    def test_nav_ru_open_ppe(self) -> None:
        result = compile_command_text("Открой СИЗ")
        assert result is not None
        self.assertEqual(result.draft.intent, AiIntentKind.NAVIGATE_SECTION)
        self.assertEqual(result.draft.section_key, "ppe")

    def test_nav_ru_show_ziz(self) -> None:
        result = compile_command_text("Выведи раздел ЗИЗ")
        assert result is not None
        self.assertEqual(result.draft.intent, AiIntentKind.NAVIGATE_SECTION)
        self.assertEqual(result.draft.section_key, "ppe")

    def test_problem_trainings_list_not_employees_nav(self) -> None:
        result = compile_command_text("Покажи сотрудников с проблемными инструктажами")
        assert result is not None
        self.assertEqual(result.draft.intent, AiIntentKind.QUERY_MODULE_STATUS)
        self.assertEqual(result.draft.module_key, "trainings")
        self.assertEqual(result.draft.filter_key, "warning")

    def test_unclosed_training_list_query(self) -> None:
        result = compile_command_text("У кого из сотрудников не закрыт инструктаж?")
        assert result is not None
        self.assertEqual(result.draft.intent, AiIntentKind.QUERY_MODULE_STATUS)
        self.assertEqual(result.draft.module_key, "trainings")
        self.assertEqual(result.draft.filter_key, "warning")

    def test_ppe_issue_ru_name_not_verb(self) -> None:
        command = "Выдай каску Лысенко Ирине Викторовне сегодняшней датой."
        result = compile_command_text(command)
        assert result is not None
        self.assertEqual(result.draft.intent, AiIntentKind.CREATE_PPE_ISSUANCE)
        self.assertIn("Лысенко", result.draft.employee_query or "")
        self.assertNotIn("Выдай", result.draft.employee_query or "")


if __name__ == "__main__":
    unittest.main()
