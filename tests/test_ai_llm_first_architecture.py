import unittest
from dataclasses import replace
from unittest.mock import patch

from osah.application.services.ai.build_ai_llm_user_prompt import should_attach_registry_hints
from osah.application.services.ai.build_ai_read_system_prompt import build_ai_read_system_prompt
from osah.application.services.ai.build_ai_semantic_system_prompt import build_ai_semantic_system_prompt
from osah.application.services.ai.build_ai_unified_system_prompt import build_ai_unified_system_prompt
from osah.application.services.ai.estimate_llm_prompt_tokens import estimate_llm_prompt_tokens, is_llm_prompt_over_budget
from osah.application.services.ai.resolve_user_ai_command import resolve_user_ai_command
from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.ai_command_resolution_status import AiCommandResolutionStatus
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.services.ai.classify_ai_resolution_track import is_write_resolution_track
from osah.domain.services.ai.compiler.compile_ai_command import compile_command_text
from osah.domain.services.ai.semantic.adapt_semantic_draft_to_command_draft import adapt_semantic_draft_to_command_draft
from osah.domain.entities.ai_semantic_audience_spec import AiSemanticAudienceSpec
from osah.domain.entities.ai_semantic_audience_type import AiSemanticAudienceType
from osah.domain.entities.ai_semantic_draft import AiSemanticDraft
from osah.domain.entities.ai_semantic_intent import AiSemanticIntent
from osah.domain.entities.ai_semantic_mode import AiSemanticMode
from osah.domain.entities.ai_semantic_module import AiSemanticModule
from osah.domain.entities.ai_semantic_payload import AiSemanticPayload
from osah.domain.entities.ai_item_draft import AiItemDraft
from osah.domain.entities.ai_bulk_audience_spec import AiBulkAudienceSpec
from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.services.ai.compiler.compile_ai_command import compile_ai_command


class AiRuntimeContextBudgetTests(unittest.TestCase):
    def test_write_prompt_is_smaller_than_legacy_combo(self) -> None:
        write_prompt = build_ai_unified_system_prompt(
            "выдай всем работникам Сварочного участка защитные очки"
        )
        read_prompt = build_ai_unified_system_prompt("Покажи просроченные инструктажи")
        self.assertLess(len(write_prompt), 4500)
        self.assertIn("Зварювальна дільниця", build_ai_semantic_system_prompt())
        self.assertNotIn("bulk_create_ppe_issuance", read_prompt)
        self.assertIn("query_daily_focus", read_prompt)

    def test_write_prompt_token_estimate_under_budget(self) -> None:
        system_prompt = build_ai_unified_system_prompt(
            "выдай всем работникам Сварочного участка защитные очки. Дата 16.06.2026"
        )
        user_prompt = "выдай всем работникам Сварочного участка защитные очки. Дата 16.06.2026"
        self.assertLess(estimate_llm_prompt_tokens(system_prompt, user_prompt), 2000)
        self.assertFalse(is_llm_prompt_over_budget(system_prompt, user_prompt))


class AiWriteFailClosedTests(unittest.TestCase):
    def test_write_track_detected_for_welding_bulk_ppe(self) -> None:
        command = "выдай всем работникам Сварочного участка защитные очки. Дата выдачи 16.06.2026"
        self.assertTrue(is_write_resolution_track(command))

    def test_compile_without_write_fallback_does_not_invent_department(self) -> None:
        command = "выдай всем работникам Сварочного участка защитные очки. Дата выдачи 16.06.2026"
        result = compile_command_text(command, allow_write_fallback=False)
        self.assertIsNotNone(result)
        assert result is not None
        self.assertTrue(result.needs_llm)
        spec = result.draft.bulk_audience_spec
        if spec is not None and spec.department_query:
            self.assertNotIn("очки", spec.department_query.lower())

    @patch("osah.application.services.ai.resolve_user_ai_command.is_ai_runtime_bundle_available", return_value=True)
    @patch("osah.application.services.ai.resolve_user_ai_command._resolve_with_llm", return_value=None)
    def test_write_command_fail_closed_after_llm_error(self, _llm, _runtime) -> None:
        resolution = resolve_user_ai_command(
            "выдай всем работникам Сварочного участка защитные очки. Дата 16.06.2026",
            access_role=AccessRole.INSPECTOR,
        )
        self.assertEqual(resolution.status, AiCommandResolutionStatus.LLM_UNAVAILABLE)
        spec = resolution.draft.bulk_audience_spec if resolution.draft else None
        if spec is not None and spec.department_query:
            self.assertNotIn("очки", spec.department_query.lower())


class AiSemanticBulkPpeTests(unittest.TestCase):
    def test_semantic_adapt_welding_department_bulk_ppe(self) -> None:
        semantic = AiSemanticDraft(
            intent=AiSemanticIntent.CREATE_PPE_ISSUANCE,
            raw_command="выдай всем работникам Сварочного участка защитные очки. Дата 16.06.2026",
            module=AiSemanticModule.PPE,
            mode=AiSemanticMode.PREVIEW_THEN_CONFIRM,
            audience=AiSemanticAudienceSpec(
                audience_type=AiSemanticAudienceType.DEPARTMENT,
                department_query="Сварочного участка",
            ),
            payload=AiSemanticPayload(
                event_date="16.06.2026",
                items=(AiItemDraft(name="защитные очки", quantity=1),),
                ppe_item_query="защитные очки",
            ),
            needs_confirmation=True,
        )
        draft = adapt_semantic_draft_to_command_draft(semantic, source="llm")
        self.assertIsNotNone(draft)
        assert draft is not None
        self.assertEqual(draft.intent, AiIntentKind.BULK_CREATE_PPE_ISSUANCE)
        self.assertIsNotNone(draft.bulk_audience_spec)
        assert draft.bulk_audience_spec is not None
        self.assertEqual(draft.bulk_audience_spec.department_query, "Сварочного участка")
        self.assertEqual(draft.issue_date, "16.06.2026")

    def test_compile_preserves_llm_bulk_department_after_align(self) -> None:
        command = "выдай всем работникам Сварочного участка защитные очки. Дата выдачи 16.06.2026"
        draft = adapt_semantic_draft_to_command_draft(
            AiSemanticDraft(
                intent=AiSemanticIntent.CREATE_PPE_ISSUANCE,
                raw_command=command,
                module=AiSemanticModule.PPE,
                mode=AiSemanticMode.PREVIEW_THEN_CONFIRM,
                audience=AiSemanticAudienceSpec(
                    audience_type=AiSemanticAudienceType.DEPARTMENT,
                    department_query="Сварочного участка",
                ),
                payload=AiSemanticPayload(
                    event_date="16.06.2026",
                    items=(AiItemDraft(name="защитные очки", quantity=1),),
                    ppe_item_query="защитные очки",
                ),
                needs_confirmation=True,
            ),
            source="llm",
        )
        self.assertIsNotNone(draft)
        assert draft is not None
        compiled = compile_ai_command(replace(draft, raw_command=command))
        spec = compiled.draft.bulk_audience_spec
        self.assertIsNotNone(spec)
        assert spec is not None
        self.assertEqual(spec.department_query, "Сварочного участка")
        self.assertNotIn("очки", (spec.department_query or "").lower())

    def test_registry_hints_skipped_for_write_with_department(self) -> None:
        command = "выдай всем работникам Сварочного участка защитные очки"
        self.assertFalse(should_attach_registry_hints(command))


if __name__ == "__main__":
    unittest.main()
