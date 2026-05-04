import sqlite3
import tempfile
import unittest
from pathlib import Path

from osah.application.services.create_ppe_record import create_ppe_record
from osah.application.services.initialize_application import initialize_application
from osah.application.services.load_ppe_registry import load_ppe_registry
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class PpeProvisionStatusTests(unittest.TestCase):
    """Тести нових полів забезпечення ЗІЗ.
    Tests for PPE provision-state fields.
    """

    def test_required_not_issued_is_problem_status(self) -> None:
        """Позначає обов'язковий невиданий ЗІЗ як проблемний.
        Marks required-but-not-issued PPE as problematic.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            context = initialize_application(build_application_paths(Path(temporary_directory)))

            create_ppe_record(
                context.database_path,
                "0001",
                "Щиток",
                True,
                False,
                "2026-05-01",
                "2026-12-01",
                "1",
                "Не видано",
                provision_status="required_not_issued",
                basis_text="Норма видачі",
                basis_note="Критична нестача",
            )

            record = next(record for record in load_ppe_registry(context.database_path) if record.note_text == "Не видано")
            self.assertEqual(record.status.value, "not_issued")
            self.assertEqual(record.provision_status.value, "required_not_issued")
            self.assertEqual(record.basis_text, "Норма видачі")
            self.assertEqual(record.basis_note, "Критична нестача")
            shut_down_logging()

    def test_issued_ppe_uses_replacement_date_logic(self) -> None:
        """Залишає чинною поточну логику строку заміни для виданого ЗІЗ.
        Keeps replacement-date logic for issued PPE.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            context = initialize_application(build_application_paths(Path(temporary_directory)))

            create_ppe_record(
                context.database_path,
                "0001",
                "Окуляри",
                True,
                True,
                "2024-01-01",
                "2024-02-01",
                "1",
                "Протерміновано",
                provision_status="issued",
            )

            record = next(record for record in load_ppe_registry(context.database_path) if record.note_text == "Протерміновано")
            self.assertEqual(record.status.value, "expired")
            shut_down_logging()

    def test_not_required_ppe_does_not_create_expiry_problem(self) -> None:
        """Не створює прострочку для ЗІЗ, який не потрібен.
        Does not create expiry problems for PPE marked as not required.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            context = initialize_application(build_application_paths(Path(temporary_directory)))

            create_ppe_record(
                context.database_path,
                "0001",
                "Фартух",
                False,
                False,
                "2024-01-01",
                "2024-02-01",
                "1",
                "Не потрібен",
                provision_status="not_required",
            )

            record = next(record for record in load_ppe_registry(context.database_path) if record.note_text == "Не потрібен")
            self.assertEqual(record.status.value, "current")
            connection = sqlite3.connect(context.database_path)
            rows = connection.execute(
                "SELECT COUNT(*) FROM notifications WHERE source_module = 'ppe.registry' AND message_text LIKE '%Фартух%'"
            ).fetchone()
            connection.close()
            self.assertEqual(rows[0], 0)
            shut_down_logging()

    def test_not_checked_compliance_creates_warning_but_not_critical(self) -> None:
        """Не поднимает critical по умолчанию, если соответствие не проверено.
        Does not raise critical by default when compliance is not checked.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            context = initialize_application(build_application_paths(Path(temporary_directory)))

            create_ppe_record(
                context.database_path,
                "0001",
                "Рукавиці",
                True,
                True,
                "2026-05-01",
                "2026-12-01",
                "1",
                "Без перевірки",
                provision_status="issued",
                compliance_check_state="not_checked",
            )

            connection = sqlite3.connect(context.database_path)
            rows = connection.execute(
                """
                SELECT notification_level
                FROM notifications
                WHERE source_module = 'ppe.registry' AND title_text LIKE '%Відповідність ЗІЗ не підтверджена%'
                """
            ).fetchall()
            connection.close()

            self.assertTrue(rows)
            self.assertTrue(all(row[0] == "warning" for row in rows))
            shut_down_logging()


if __name__ == "__main__":
    unittest.main()
