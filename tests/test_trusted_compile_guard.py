import unittest

from osah.domain.entities.ai_bulk_audience_spec import AiBulkAudienceSpec
from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.entities.ai_item_draft import AiItemDraft
from osah.domain.services.ai.command_verb_tokens import is_employee_query_stop_word, sanitize_employee_query
from osah.domain.services.ai.compiler.compile_ai_command import compile_ai_command
from osah.domain.services.ai.demote_single_employee_bulk_draft import demote_single_employee_bulk_draft
from osah.domain.services.ai.extract_employee_query_from_command import extract_employee_query_from_command
from osah.domain.services.ai.normalize_ai_issue_date_text import normalize_ai_issue_date_text
from osah.domain.services.ai.reconcile_medical_restriction_command import reconcile_medical_restriction_command
from osah.domain.services.ai.semantic.adapt_semantic_draft_to_command_draft import adapt_semantic_draft_to_command_draft
from osah.domain.services.ai.semantic.build_ai_semantic_draft_from_command import build_ai_semantic_draft_from_command
from osah.domain.services.ai.should_preserve_trusted_semantic_slot import (
    should_block_bulk_intent_promotion,
    should_preserve_trusted_slot,
)


class TrustedCompileGuardTests(unittest.TestCase):
    def test_preserve_trusted_write_slots(self) -> None:
        draft = AiCommandDraft(
            intent=AiIntentKind.CREATE_PPE_ISSUANCE,
            raw_command="test",
            source="llm",
            employee_query="Петров",
            issue_date="сьогодні",
            training_type="repeated",
            work_risk_category="high_risk",
            ppe_item_query="каска",
            items=(AiItemDraft(name="каска", quantity=1),),
        )
        self.assertTrue(should_preserve_trusted_slot(draft, "employee_query"))
        self.assertTrue(should_preserve_trusted_slot(draft, "issue_date"))
        self.assertTrue(should_preserve_trusted_slot(draft, "training_type"))
        self.assertTrue(should_preserve_trusted_slot(draft, "work_risk_category"))
        self.assertTrue(should_preserve_trusted_slot(draft, "ppe_item_query"))
        self.assertTrue(should_preserve_trusted_slot(draft, "items"))
        self.assertTrue(should_preserve_trusted_slot(draft, "intent"))

    def test_block_bulk_promotion_for_trusted_single(self) -> None:
        draft = AiCommandDraft(
            intent=AiIntentKind.CREATE_PPE_ISSUANCE,
            raw_command="Выдай Иванову каску",
            source="llm",
            employee_query="Иванов",
        )
        self.assertTrue(should_block_bulk_intent_promotion(draft))

    def test_petrov_bulk_demoted_to_single(self) -> None:
        draft = AiCommandDraft(
            intent=AiIntentKind.BULK_CREATE_PPE_ISSUANCE,
            raw_command="Занеси Петрову каску и ботинки за сегодня",
            source="llm",
            employee_query="за",
            issue_date="сьогодні",
            ppe_item_query="каску",
            items=(
                AiItemDraft(name="каска", quantity=1),
                AiItemDraft(name="ботинки", quantity=1),
            ),
            bulk_audience_spec=AiBulkAudienceSpec(
                employee_queries=("Петров",),
                filter_key="today",
            ),
        )
        compiled = compile_ai_command(draft).draft
        self.assertEqual(compiled.intent, AiIntentKind.CREATE_PPE_ISSUANCE)
        self.assertEqual(compiled.employee_query, "Петров")
        self.assertIsNone(compiled.bulk_audience_spec)

    def test_demchenko_medical_restriction_update_path(self) -> None:
        command = "Добавь для Демченко Натальи ограничение по работе на высоте"
        draft = AiCommandDraft(
            intent=AiIntentKind.BULK_CREATE_MEDICAL_RECORD,
            raw_command=command,
            source="llm",
            employee_query="Демченко Натальи ограничение по работе на высоте",
            bulk_audience_spec=AiBulkAudienceSpec(
                employee_queries=("Добавь", "Демченко", "Натальи"),
            ),
        )
        compiled = compile_ai_command(draft).draft
        self.assertEqual(compiled.intent, AiIntentKind.UPDATE_MEDICAL_RECORD)
        self.assertIn("Демченко", compiled.employee_query or "")
        self.assertNotIn("ограничение", compiled.employee_query or "")
        self.assertIn("высоте", compiled.restriction_note or "")

    def test_stop_word_za_not_employee(self) -> None:
        self.assertTrue(is_employee_query_stop_word("за"))
        self.assertIsNone(sanitize_employee_query("за"))
        self.assertIsNone(extract_employee_query_from_command("за сегодня"))

    def test_adapt_semantic_medical_date_normalization(self) -> None:
        semantic = build_ai_semantic_draft_from_command("Добавь медосмотр Сидоренко до 15 июля")
        self.assertIsNotNone(semantic)
        assert semantic is not None
        draft = adapt_semantic_draft_to_command_draft(semantic, source="llm")
        self.assertIsNotNone(draft)
        assert draft is not None
        self.assertIsNotNone(draft.valid_until_date or draft.issue_date)

    def test_normalize_issue_date_symbolic(self) -> None:
        self.assertEqual(normalize_ai_issue_date_text("сьогодні").count("."), 2)

    def test_reconcile_medical_restriction_direct(self) -> None:
        draft = reconcile_medical_restriction_command(
            AiCommandDraft(
                intent=AiIntentKind.CREATE_MEDICAL_RECORD,
                raw_command="Добавь для Демченко ограничение по работе на высоте",
                source="llm",
            )
        )
        self.assertEqual(draft.intent, AiIntentKind.UPDATE_MEDICAL_RECORD)
        self.assertIn("высоте", draft.restriction_note or "")

    def test_demote_single_employee_bulk_direct(self) -> None:
        demoted = demote_single_employee_bulk_draft(
            AiCommandDraft(
                intent=AiIntentKind.BULK_CREATE_PPE_ISSUANCE,
                raw_command="test",
                source="llm",
                bulk_audience_spec=AiBulkAudienceSpec(employee_queries=("Петров",)),
            )
        )
        self.assertEqual(demoted.intent, AiIntentKind.CREATE_PPE_ISSUANCE)
        self.assertEqual(demoted.employee_query, "Петров")


if __name__ == "__main__":
    unittest.main()
