import unittest
from unittest import mock

from osah.application.services.ai.query_overdue_summary import query_overdue_summary
from osah.application.services.ai.search_ppe_catalog_candidates import search_ppe_catalog_candidates
from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_command_track import AiCommandTrack
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.entities.ai_item_draft import AiItemDraft
from osah.domain.services.ai.detect_ai_command_track import (
    detect_ai_command_track,
    matches_section_problems_query,
)
from osah.domain.services.ai.normalize_ai_module_key import normalize_ai_module_key
from osah.domain.services.ai.reconcile_ai_command_draft import reconcile_ai_command_draft
from osah.domain.services.ai.reconcile_ai_command_track import reconcile_ai_command_track
from osah.domain.services.ai.resolve_ppe_item_alias import resolve_ppe_item_alias
from osah.domain.services.ai.try_match_simple_ai_command import try_match_simple_ai_command


class AiTrackDetectionTests(unittest.TestCase):
    def test_write_track_for_ru_ppe_issue(self) -> None:
        draft = AiCommandDraft(
            intent=AiIntentKind.QUERY_MISSING_PPE,
            raw_command="Выдай каску сегодняшним числом для Лисенко Т.В.",
            source="llm",
            ppe_item_query="каска",
        )
        self.assertEqual(detect_ai_command_track(draft), AiCommandTrack.WRITE)

    def test_read_track_for_missing_ppe_list(self) -> None:
        draft = AiCommandDraft(
            intent=AiIntentKind.QUERY_MISSING_PPE,
            raw_command="Кому потрібні каски?",
            source="llm",
            ppe_item_query="каска",
        )
        self.assertEqual(detect_ai_command_track(draft), AiCommandTrack.READ)

    def test_section_problems_pattern(self) -> None:
        self.assertTrue(matches_section_problems_query("які зараз є проблемні розділи?"))


class AiTrackReconcileTests(unittest.TestCase):
    def test_write_query_promoted_to_ppe_issuance(self) -> None:
        draft = reconcile_ai_command_draft(
            AiCommandDraft(
                intent=AiIntentKind.QUERY_MISSING_PPE,
                raw_command="Выдай каску сегодняшним числом для Лисенко Т.В.",
                source="llm",
                ppe_item_query="каска",
            )
        )
        self.assertEqual(draft.intent, AiIntentKind.CREATE_PPE_ISSUANCE)
        self.assertEqual(draft.employee_query, "Лисенко Т.В.")
        self.assertEqual(draft.issue_date, "сьогодні")
        self.assertTrue(draft.needs_confirmation)
        self.assertEqual(len(draft.items), 1)

    def test_section_problems_intent(self) -> None:
        draft = reconcile_ai_command_draft(
            AiCommandDraft(
                intent=AiIntentKind.QUERY_OVERDUE_SUMMARY,
                raw_command="які зараз є проблемні розділи?",
                source="llm",
                module_key="проблемні",
            )
        )
        self.assertEqual(draft.intent, AiIntentKind.QUERY_SECTION_PROBLEMS)

    def test_readiness_not_overridden_by_write(self) -> None:
        draft = reconcile_ai_command_draft(
            AiCommandDraft(
                intent=AiIntentKind.QUERY_MISSING_PPE,
                raw_command="Що потрібно для Білик",
                source="llm",
                employee_query="Білик",
            )
        )
        self.assertEqual(draft.intent, AiIntentKind.QUERY_EMPLOYEE_READINESS)


class AiRouterSectionProblemsTests(unittest.TestCase):
    def test_section_problems_router(self) -> None:
        draft = try_match_simple_ai_command("які зараз є проблемні розділи?")
        self.assertIsNotNone(draft)
        assert draft is not None
        self.assertEqual(draft.intent, AiIntentKind.QUERY_SECTION_PROBLEMS)


class AiModuleKeyNormalizeTests(unittest.TestCase):
    def test_unknown_module_key_falls_back_to_all(self) -> None:
        self.assertEqual(normalize_ai_module_key("проблемні"), "all")

    def test_overdue_summary_uses_all_for_garbage_key(self) -> None:
        with mock.patch(
            "osah.application.services.ai.query_overdue_summary.load_ppe_registry",
            return_value=[],
        ):
            with mock.patch(
                "osah.application.services.ai.query_overdue_summary.load_training_registry",
                return_value=[],
            ):
                with mock.patch(
                    "osah.application.services.ai.query_overdue_summary.load_medical_registry",
                    return_value=[],
                ):
                    with mock.patch(
                        "osah.application.services.ai.query_overdue_summary.load_work_permit_registry",
                        return_value=[],
                    ):
                        from pathlib import Path

                        result_all = query_overdue_summary(Path("test.db"), "all")
                        result_garbage = query_overdue_summary(Path("test.db"), "проблемні")
                        self.assertEqual(result_all, result_garbage)


class AiPpeAliasTests(unittest.TestCase):
    def test_footwear_alias(self) -> None:
        self.assertEqual(resolve_ppe_item_alias("взуття"), "Черевики захисні")

    def test_track_reconcile_enriches_items(self) -> None:
        draft = reconcile_ai_command_track(
            AiCommandDraft(
                intent=AiIntentKind.CREATE_PPE_ISSUANCE,
                raw_command="Выдай каску для Петренко",
                source="llm",
            )
        )
        self.assertEqual(draft.employee_query, "Петренко")
        self.assertEqual(len(draft.items), 1)
        self.assertEqual(draft.items[0].name, "каску")


if __name__ == "__main__":
    unittest.main()
