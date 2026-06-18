import unittest

from osah.application.services.ai.build_ai_operation_plan import build_ai_operation_plan
from osah.domain.entities.ai_bulk_audience_spec import AiBulkAudienceSpec
from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.entities.ai_item_draft import AiItemDraft
from osah.domain.entities.ai_operation_plan_kind import AiOperationPlanKind
from osah.domain.entities.ai_semantic_mode import AiSemanticMode


class AiOperationPlanTests(unittest.TestCase):
    def test_query_plan_is_read_only_answer(self) -> None:
        plan = build_ai_operation_plan(
            AiCommandDraft(
                intent=AiIntentKind.QUERY_DAILY_FOCUS,
                raw_command="Что закрыть сегодня?",
                source="test",
            )
        )

        self.assertEqual(plan.kind, AiOperationPlanKind.ANSWER)
        self.assertEqual(plan.mode, AiSemanticMode.READ_ONLY)
        self.assertFalse(plan.requires_confirmation)
        self.assertTrue(plan.can_execute)

    def test_single_write_requires_confirmation(self) -> None:
        plan = build_ai_operation_plan(
            AiCommandDraft(
                intent=AiIntentKind.CREATE_PPE_ISSUANCE,
                raw_command="Занеси Петрову каску сегодня",
                source="test",
                employee_query="Петров",
                items=(AiItemDraft(name="каска", quantity=1),),
                issue_date="сьогодні",
                needs_confirmation=True,
            )
        )

        self.assertEqual(plan.kind, AiOperationPlanKind.SINGLE_WRITE)
        self.assertEqual(plan.mode, AiSemanticMode.CONFIRM_THEN_EXECUTE)
        self.assertTrue(plan.requires_confirmation)
        self.assertFalse(plan.requires_preview)
        self.assertTrue(plan.can_execute)

    def test_bulk_write_requires_preview_and_confirmation(self) -> None:
        plan = build_ai_operation_plan(
            AiCommandDraft(
                intent=AiIntentKind.BULK_CREATE_PPE_ISSUANCE,
                raw_command="Выдай подразделению Склад перчатки",
                source="test",
                bulk_audience_spec=AiBulkAudienceSpec(department_query="Склад"),
                items=(AiItemDraft(name="перчатки", quantity=1),),
                issue_date="сьогодні",
                needs_confirmation=True,
            )
        )

        self.assertEqual(plan.kind, AiOperationPlanKind.BULK_WRITE)
        self.assertEqual(plan.mode, AiSemanticMode.PREVIEW_THEN_CONFIRM)
        self.assertTrue(plan.requires_preview)
        self.assertTrue(plan.requires_confirmation)
        self.assertTrue(plan.can_execute)

    def test_bulk_without_audience_is_blocked_for_clarification(self) -> None:
        plan = build_ai_operation_plan(
            AiCommandDraft(
                intent=AiIntentKind.BULK_CREATE_PPE_ISSUANCE,
                raw_command="Выдай всем перчатки",
                source="test",
                items=(AiItemDraft(name="перчатки", quantity=1),),
                issue_date="сьогодні",
                needs_confirmation=True,
            )
        )

        self.assertEqual(plan.kind, AiOperationPlanKind.BULK_WRITE)
        self.assertFalse(plan.can_execute)
        self.assertTrue(plan.issues)

    def test_unknown_intent_is_unsupported(self) -> None:
        plan = build_ai_operation_plan(
            AiCommandDraft(
                intent=AiIntentKind.UNKNOWN,
                raw_command="Сделай что-нибудь",
                source="test",
            )
        )

        self.assertEqual(plan.kind, AiOperationPlanKind.UNSUPPORTED)
        self.assertEqual(plan.mode, AiSemanticMode.UNSUPPORTED)
        self.assertFalse(plan.can_execute)
        self.assertTrue(plan.issues)


if __name__ == "__main__":
    unittest.main()
