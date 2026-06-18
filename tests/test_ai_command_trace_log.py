import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from osah.domain.entities.ai_command_draft import AiCommandDraft
from osah.domain.entities.ai_intent_kind import AiIntentKind
from osah.infrastructure.config.application_paths import ApplicationPaths
from osah.infrastructure.logging.append_ai_command_trace import (
    append_ai_command_trace_step,
    begin_ai_command_trace,
    end_ai_command_trace,
)


class AiCommandTraceLogTests(unittest.TestCase):
    def test_trace_writes_pipeline_steps(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            paths = ApplicationPaths(
                project_root=root,
                data_directory=root / "data",
                log_directory=root / "logs",
                database_file_path=root / "data" / "osah.sqlite3",
                log_file_path=root / "logs" / "osah.log",
            )
            log_path = paths.log_directory / "ai_command_trace.log"
            with patch("osah.infrastructure.logging.append_ai_command_trace.is_ai_command_trace_enabled", return_value=True), patch(
                "osah.infrastructure.logging.append_ai_command_trace.build_ai_command_trace_log_path",
                return_value=log_path,
            ):
                trace_id = begin_ai_command_trace("Занеси первичный инструктаж Кравченко")
                append_ai_command_trace_step(trace_id, "LLM_DRAFT", payload={"intent": "update_training_record"})
                append_ai_command_trace_step(trace_id, "RECONCILE", detail="update_training_record → create_training_record")
                end_ai_command_trace(trace_id, outcome="success")

            content = log_path.read_text(encoding="utf-8")
            self.assertIn("TRACE ", content)
            self.assertIn("USER: Занеси первичный инструктаж Кравченко", content)
            self.assertIn("[LLM_DRAFT]", content)
            self.assertIn("[RECONCILE]", content)
            self.assertIn("TRACE_END", content)


if __name__ == "__main__":
    unittest.main()
