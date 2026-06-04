import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from osah.infrastructure.config.is_demo_seed_enabled import is_demo_seed_enabled


class IsDemoSeedEnabledTests(unittest.TestCase):
    """Тести визначення demo-режиму за маркером або змінною середовища."""

    def test_returns_true_when_env_flag_set(self) -> None:
        with patch.dict(os.environ, {"OSAH_ENABLE_DEMO_SEED": "1"}, clear=False):
            self.assertTrue(is_demo_seed_enabled())

    def test_returns_true_when_marker_file_exists(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            project_root = Path(temporary_directory)
            (project_root / "ClearWork.demo").write_text("", encoding="utf-8")
            with patch.dict(os.environ, {}, clear=True):
                with patch(
                    "osah.infrastructure.config.is_demo_seed_enabled.build_application_paths"
                ) as build_paths:
                    from osah.infrastructure.config.application_paths import build_application_paths

                    build_paths.return_value = build_application_paths(project_root)
                    self.assertTrue(is_demo_seed_enabled())


if __name__ == "__main__":
    unittest.main()
