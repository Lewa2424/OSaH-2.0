import tempfile
import unittest
from pathlib import Path

from osah.application.services.initialize_application import initialize_application
from osah.application.services.visual.load_visual_alert_state import load_visual_alert_state
from osah.application.services.visual.mark_critical_attention_shake import mark_critical_attention_shake
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class LoadVisualAlertStateTests(unittest.TestCase):
    """Тести стану візуальної сигналізації shell.
    Тесты состояния визуальной сигнализации shell.
    """

    # ###### ПЕРЕВІРКА THROTTLING ДЛЯ CRITICAL-SHAKE / ПРОВЕРКА THROTTLING ДЛЯ CRITICAL-SHAKE ######
    def test_load_visual_alert_state_disables_shake_after_mark(self) -> None:
        """Перевіряє, що після фіксації shake система не просить запускати його повторно одразу.
        Проверяет, что после фиксации shake система не просит запускать его повторно сразу.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)

            initial_visual_alert_state = load_visual_alert_state(context.database_path)
            self.assertTrue(initial_visual_alert_state.should_shake)

            mark_critical_attention_shake(context.database_path)
            throttled_visual_alert_state = load_visual_alert_state(context.database_path)

            self.assertFalse(throttled_visual_alert_state.should_shake)
            shut_down_logging()


if __name__ == "__main__":
    unittest.main()
