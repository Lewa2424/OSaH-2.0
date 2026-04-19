import tempfile
import unittest
from pathlib import Path

from osah.application.services.initialize_application import initialize_application
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class LoadDashboardSnapshotTests(unittest.TestCase):
    """Тести стартового зведення головного екрана.
    Тесты стартовой сводки главного экрана.
    """

    # ###### ПЕРЕВІРКА СТАРТОВОГО ЗВЕДЕННЯ / ПРОВЕРКА СТАРТОВОЙ СВОДКИ ######
    def test_initialize_application_returns_seeded_snapshot(self) -> None:
        """Перевіряє, що стартовий знімок містить очікувані демодані.
        Проверяет, что стартовый снимок содержит ожидаемые демоданные.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)

            self.assertGreaterEqual(context.dashboard_snapshot.employee_total, 50)
            self.assertGreater(context.dashboard_snapshot.critical_items, 0)
            self.assertGreater(context.dashboard_snapshot.warning_items, 0)
            self.assertGreater(len(context.dashboard_snapshot.active_notifications), 10)
            self.assertEqual(context.dashboard_snapshot.unread_news_total, 0)
            self.assertEqual(len(context.dashboard_snapshot.latest_news_items), 0)
            shut_down_logging()


if __name__ == "__main__":
    unittest.main()
