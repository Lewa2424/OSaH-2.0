import os
import tempfile
import unittest
from pathlib import Path

from osah.application.services.ai.build_ai_llm_user_prompt import (
    build_ai_llm_user_prompt,
    command_needs_registry_hints,
)
from osah.application.services.ai.build_ai_registry_hints import build_ai_registry_hints
from osah.application.services.initialize_application import initialize_application
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class RegistryHintsTests(unittest.TestCase):
    def test_command_needs_registry_hints_for_department_phrase(self) -> None:
        self.assertTrue(command_needs_registry_hints("Кто работает в подразделении Лаборатория?"))
        self.assertFalse(command_needs_registry_hints("Покажи просроченные инструктажи"))

    def test_registry_hints_are_compact(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            try:
                os.environ["OSAH_ENABLE_DEMO_SEED"] = "1"
                application_paths = build_application_paths(Path(temporary_directory))
                context = initialize_application(application_paths)
                hints = build_ai_registry_hints(context.database_path)
                self.assertLessEqual(len(hints), 600)
                self.assertIn("departments", hints)
                self.assertIn("positions", hints)
            finally:
                shut_down_logging()

    def test_llm_user_prompt_includes_registry_hints_conditionally(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            try:
                os.environ["OSAH_ENABLE_DEMO_SEED"] = "1"
                application_paths = build_application_paths(Path(temporary_directory))
                context = initialize_application(application_paths)
                with_hints = build_ai_llm_user_prompt(
                    "Кто работает в службе охраны труда?",
                    database_path=context.database_path,
                )
                without_hints = build_ai_llm_user_prompt(
                    "Покажи просроченные инструктажи",
                    database_path=context.database_path,
                )
                self.assertIn("[registry_hints]", with_hints)
                self.assertNotIn("[registry_hints]", without_hints)
            finally:
                shut_down_logging()


if __name__ == "__main__":
    unittest.main()
