import unittest

from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.entities.ai_semantic_audience_type import AiSemanticAudienceType
from osah.domain.entities.ai_semantic_condition_type import AiSemanticConditionType
from osah.domain.entities.ai_semantic_intent import AiSemanticIntent
from osah.domain.entities.ai_semantic_mode import AiSemanticMode
from osah.domain.services.ai.compiler.compile_ai_command import compile_command_text
from osah.domain.services.ai.semantic.build_ai_semantic_draft_from_command import build_ai_semantic_draft_from_command


class AiSemanticDraftExamplesTests(unittest.TestCase):
    def test_department_ppe_command_builds_semantic_bulk_audience(self) -> None:
        draft = build_ai_semantic_draft_from_command(
            "Выдай подразделению Склад и логистика по 1 паре перчаток с сегодняшней даты"
        )

        self.assertIsNotNone(draft)
        assert draft is not None
        self.assertEqual(draft.intent, AiSemanticIntent.CREATE_PPE_ISSUANCE)
        self.assertEqual(draft.mode, AiSemanticMode.PREVIEW_THEN_CONFIRM)
        self.assertEqual(draft.audience.audience_type, AiSemanticAudienceType.DEPARTMENT)
        self.assertEqual(draft.audience.department_query, "Склад и логистика")
        self.assertEqual(tuple(item.name for item in draft.payload.items), ("перчатки",))
        self.assertEqual(draft.payload.event_date, "сьогодні")

    def test_department_ppe_command_compiles_to_current_bulk_draft(self) -> None:
        result = compile_command_text(
            "Выдай подразделению Склад и логистика по 1 паре перчаток с сегодняшней даты"
        )

        self.assertIsNotNone(result)
        assert result is not None
        self.assertFalse(result.needs_llm)
        self.assertEqual(result.draft.intent, AiIntentKind.BULK_CREATE_PPE_ISSUANCE)
        self.assertIsNotNone(result.draft.bulk_audience_spec)
        assert result.draft.bulk_audience_spec is not None
        self.assertEqual(result.draft.bulk_audience_spec.department_query, "Склад и логистика")
        self.assertEqual(tuple(item.name for item in result.draft.items), ("перчатки",))

    def test_work_permit_participants_ppe_keeps_skip_duplicate_condition(self) -> None:
        draft = build_ai_semantic_draft_from_command(
            "Выдай всем участникам наряда 22 по паре перчаток и каске, если у них нет действующей выдачи."
        )

        self.assertIsNotNone(draft)
        assert draft is not None
        self.assertEqual(draft.intent, AiSemanticIntent.CREATE_PPE_ISSUANCE_FOR_WORK_PERMIT_PARTICIPANTS)
        self.assertEqual(draft.audience.audience_type, AiSemanticAudienceType.WORK_PERMIT_PARTICIPANTS)
        self.assertEqual(draft.audience.permit_number, "22")
        self.assertIn(
            AiSemanticConditionType.SKIP_IF_ACTIVE_PPE_EXISTS,
            tuple(condition.condition_type for condition in draft.conditions),
        )

    def test_employee_transfer_batch_preserves_do_not_change_position_condition(self) -> None:
        draft = build_ai_semantic_draft_from_command(
            "Переведи Иванова и Сидоренко на участок ППК-2 с понедельника, должности не менять."
        )

        self.assertIsNotNone(draft)
        assert draft is not None
        self.assertEqual(draft.intent, AiSemanticIntent.UPDATE_EMPLOYEE_SITE_BATCH)
        self.assertEqual(draft.audience.employee_queries, ("Иванова", "Сидоренко"))
        self.assertEqual(draft.payload.department_name, "ППК-2")
        self.assertEqual(draft.payload.effective_date, "next_monday")
        self.assertIn(
            AiSemanticConditionType.DO_NOT_CHANGE_POSITION,
            tuple(condition.condition_type for condition in draft.conditions),
        )

    def test_employee_cleanup_is_read_only(self) -> None:
        draft = build_ai_semantic_draft_from_command(
            "Найди сотрудников без участка или должности и подготовь мне список на исправление."
        )

        self.assertIsNotNone(draft)
        assert draft is not None
        self.assertEqual(draft.intent, AiSemanticIntent.PREPARE_EMPLOYEE_DATA_CLEANUP)
        self.assertEqual(draft.mode, AiSemanticMode.READ_ONLY)
        self.assertIn("missing_department", draft.audience.filters)
        self.assertIn("missing_position", draft.audience.filters)

    def test_medical_batch_extracts_employee_list(self) -> None:
        draft = build_ai_semantic_draft_from_command(
            "Обнови медосмотр Петрову, Иванову и Коваленко: прошли вчера, срок действия до конца следующего года."
        )

        self.assertIsNotNone(draft)
        assert draft is not None
        self.assertEqual(draft.intent, AiSemanticIntent.UPDATE_MEDICAL_BATCH)
        self.assertEqual(draft.audience.employee_queries, ("Петрову", "Иванову", "Коваленко"))
        self.assertEqual(draft.payload.event_date, "вчора")
        self.assertEqual(draft.payload.valid_until_date, "end_of_next_year")


if __name__ == "__main__":
    unittest.main()
