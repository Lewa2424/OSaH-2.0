import os
import tempfile
import unittest
from pathlib import Path

from osah.application.services.ai.prepare_ai_command_text_for_resolution import prepare_ai_command_text_for_resolution
from osah.application.services.ai.resolve_department_from_registry import resolve_department_from_registry
from osah.application.services.initialize_application import initialize_application
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.domain.services.ai.build_unknown_intent_clarification_message import build_unknown_intent_clarification_message
from osah.domain.services.ai.compiler.compile_ai_command import compile_command_text
from osah.domain.services.ai.match_department_name_query import department_name_matches_query
from osah.domain.services.ai.normalize_ai_command_text import normalize_ai_command_text
from osah.domain.services.ai.registry_tokens_typo_match import registry_tokens_typo_match
from osah.domain.services.ai.try_match_simple_ai_command import try_match_simple_ai_command
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class AiCommandNormalizationTests(unittest.TestCase):
    def test_marker_typo_pakazhi_routes_to_daily_focus(self) -> None:
        normalized = normalize_ai_command_text("Пакажи критичні проблеми")
        draft = try_match_simple_ai_command(normalized)
        self.assertIsNotNone(draft)
        assert draft is not None
        self.assertEqual(draft.intent, AiIntentKind.QUERY_OVERDUE_SUMMARY)

    def test_synonym_otobrazi_routes_like_pokazhi(self) -> None:
        normalized = normalize_ai_command_text("Отобрази критичні проблеми")
        draft = try_match_simple_ai_command(normalized)
        self.assertIsNotNone(draft)
        assert draft is not None
        self.assertEqual(draft.intent, AiIntentKind.QUERY_OVERDUE_SUMMARY)

    def test_compile_preserves_original_raw_command(self) -> None:
        result = compile_command_text("Пакажи критичні проблеми")
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.draft.raw_command, "Пакажи критичні проблеми")
        self.assertEqual(result.draft.intent, AiIntentKind.QUERY_OVERDUE_SUMMARY)

    def test_unknown_hint_contains_examples(self) -> None:
        message = build_unknown_intent_clarification_message("сделай что-нибудь с касками")
        self.assertIn("каск", message.lower())
        self.assertIn("наприклад", message.lower())


class RegistryTypoMatchTests(unittest.TestCase):
    def test_single_char_typo_matches_department_token(self) -> None:
        self.assertTrue(registry_tokens_typo_match("лабора", "лаборо"))
        self.assertTrue(
            department_name_matches_query("Цех лаборатории N1", "лабораториа"),
        )

    def test_russian_welding_section_matches_ukrainian_department(self) -> None:
        self.assertTrue(
            department_name_matches_query("Зварювальна дільниця", "Сварочного участка"),
        )
        self.assertTrue(
            department_name_matches_query("Зварювальна дільниця", "сварочный участок"),
        )

    def test_grounding_resolves_russian_welding_section(self) -> None:
        resolution = resolve_department_from_registry(
            build_application_paths().database_file_path,
            "Сварочного участка",
        )
        self.assertEqual(resolution.status, "resolved")
        self.assertEqual(resolution.canonical_name, "Зварювальна дільниця")

    def test_grounding_resolves_department_with_typo(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            try:
                os.environ["OSAH_ENABLE_DEMO_SEED"] = "1"
                application_paths = build_application_paths(Path(temporary_directory))
                context = initialize_application(application_paths)
                resolution = resolve_department_from_registry(context.database_path, "Лабораториа")
                self.assertEqual(resolution.status, "resolved")
            finally:
                shut_down_logging()


class PrepareCommandTextTests(unittest.TestCase):
    def test_prepare_applies_normalize_without_database(self) -> None:
        original, prepared = prepare_ai_command_text_for_resolution("Пакажи просроченные инструктажи")
        self.assertEqual(original, "Пакажи просроченные инструктажи")
        self.assertEqual(prepared, "Покажи просроченные инструктажи")


if __name__ == "__main__":
    unittest.main()
