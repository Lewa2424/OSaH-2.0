import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from osah.application.services.security.security_setting_keys import DEMO_DISTRIBUTION_ENABLED
from osah.infrastructure.config.is_demo_timed_distribution_enabled import (
    is_demo_timed_distribution_enabled_in_settings,
    is_demo_timed_distribution_marker_present,
)
from osah.infrastructure.config.is_demo_seed_enabled import is_demo_seed_enabled


class IsDemoTimedDistributionEnabledTests(unittest.TestCase):
    """Тести визначення demo-only дистрибуції з таймером."""

    def test_returns_true_when_env_flag_set(self) -> None:
        with patch.dict(os.environ, {"OSAH_ENABLE_DEMO_TIMED": "1"}, clear=False):
            self.assertTrue(is_demo_timed_distribution_marker_present())

    def test_returns_true_when_timed_marker_file_exists(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            project_root = Path(temporary_directory)
            (project_root / "ClearWork.demo_timed").write_text("timed", encoding="utf-8")
            with patch.dict(os.environ, {}, clear=True):
                self.assertTrue(is_demo_timed_distribution_marker_present(project_root))

    def test_demo_seed_marker_does_not_enable_timed_distribution(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            project_root = Path(temporary_directory)
            (project_root / "ClearWork.demo").write_text("demo", encoding="utf-8")
            with patch.dict(os.environ, {}, clear=True):
                with patch(
                    "osah.infrastructure.config.is_demo_seed_enabled.build_application_paths"
                ) as build_paths:
                    from osah.infrastructure.config.application_paths import build_application_paths

                    build_paths.return_value = build_application_paths(project_root)
                    self.assertTrue(is_demo_seed_enabled())
                self.assertFalse(is_demo_timed_distribution_marker_present(project_root))

    def test_returns_true_when_distribution_flag_in_settings(self) -> None:
        self.assertTrue(
            is_demo_timed_distribution_enabled_in_settings({DEMO_DISTRIBUTION_ENABLED: "1"})
        )


if __name__ == "__main__":
    unittest.main()
