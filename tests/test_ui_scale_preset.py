import tempfile
import unittest
from pathlib import Path

from osah.application.services.initialize_application import initialize_application
from osah.application.services.load_ui_scale_preset import load_ui_scale_preset
from osah.application.services.save_ui_scale_preset import save_ui_scale_preset
from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.ui_scale_preset import UiScalePreset
from osah.domain.errors.access_denied_error import AccessDeniedError
from osah.domain.services.parse_ui_scale_preset import parse_ui_scale_preset
from osah.domain.services.resolve_ui_scale_factor import resolve_ui_scale_factor
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class UiScalePresetTests(unittest.TestCase):
    """Тести пресетів масштабу інтерфейсу.
    Tests for UI scale presets.
    """

    def test_parse_ui_scale_preset_defaults_to_compact(self) -> None:
        """Повертає compact для порожнього або невідомого значення.
        Returns compact for empty or unknown values.
        """

        self.assertEqual(parse_ui_scale_preset(None), UiScalePreset.COMPACT)
        self.assertEqual(parse_ui_scale_preset(""), UiScalePreset.COMPACT)
        self.assertEqual(parse_ui_scale_preset("unknown"), UiScalePreset.COMPACT)

    def test_resolve_ui_scale_factor_returns_expected_values(self) -> None:
        """Перевіряє коефіцієнти для всіх пресетів.
        Checks scale factors for all presets.
        """

        self.assertEqual(resolve_ui_scale_factor(UiScalePreset.COMPACT), 1.0)
        self.assertEqual(resolve_ui_scale_factor(UiScalePreset.NORMAL), 1.15)
        self.assertEqual(resolve_ui_scale_factor(UiScalePreset.LARGE), 1.25)
        self.assertEqual(resolve_ui_scale_factor(UiScalePreset.XLARGE), 1.35)

    def test_save_ui_scale_preset_persists_for_inspector_and_manager(self) -> None:
        """Зберігає пресет для inspector і manager.
        Persists the preset for inspector and manager roles.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)

            save_ui_scale_preset(
                context.database_path,
                UiScalePreset.LARGE,
                access_role=AccessRole.INSPECTOR,
            )
            self.assertEqual(load_ui_scale_preset(context.database_path), UiScalePreset.LARGE)

            save_ui_scale_preset(
                context.database_path,
                UiScalePreset.NORMAL,
                access_role=AccessRole.MANAGER,
            )
            self.assertEqual(load_ui_scale_preset(context.database_path), UiScalePreset.NORMAL)
            shut_down_logging()

    def test_save_ui_scale_preset_rejects_unknown_role(self) -> None:
        """Відхиляє збереження для невідомої ролі.
        Rejects saving for an unknown role.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)

            class UnknownRole:
                value = "unknown"

            with self.assertRaises(AccessDeniedError):
                save_ui_scale_preset(
                    context.database_path,
                    UiScalePreset.NORMAL,
                    access_role=UnknownRole(),  # type: ignore[arg-type]
                )
            shut_down_logging()


if __name__ == "__main__":
    unittest.main()
