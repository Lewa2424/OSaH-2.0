import tempfile
import unittest
from pathlib import Path

from osah.application.services.initialize_application import initialize_application
from osah.application.services.sync_control_notifications import sync_control_notifications
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.database.create_database_connection import create_database_connection
from osah.infrastructure.database.queries.list_notifications import list_notifications
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class SyncControlNotificationsTests(unittest.TestCase):
    """Тесты синхронизации контрольных уведомлений.
    Tests for control-notification synchronization.
    """

    def test_sync_control_notifications_persists_active_notifications(self) -> None:
        """Проверяет, что синхронизация записывает активные уведомления в БД.
        Checks that synchronization writes active notifications into the database.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)
            connection = create_database_connection(context.database_path)
            connection.execute(
                """
                INSERT INTO employees (
                    personnel_number,
                    full_name,
                    position_name,
                    department_name,
                    employment_status
                )
                VALUES (?, ?, ?, ?, ?);
                """,
                ("1003", "Неповний Працівник", "Монтажник", "", "active"),
            )
            connection.commit()

            sync_control_notifications(connection)
            notifications = list_notifications(connection)

            connection.close()
            self.assertTrue(any(notification.title_text == "Не заповнений підрозділ" for notification in notifications))
            self.assertTrue(any(notification.title_text == "Відсутній первинний інструктаж" for notification in notifications))
            shut_down_logging()


if __name__ == "__main__":
    unittest.main()
