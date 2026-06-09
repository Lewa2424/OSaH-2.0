import tempfile
import unittest
from pathlib import Path
import zipfile

from osah.application.services.build_and_save_manual_daily_report import build_and_save_manual_daily_report
from osah.application.services.initialize_application import initialize_application
from osah.application.services.load_audit_log_entries import load_audit_log_entries
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging
from osah.domain.entities.access_role import AccessRole


class BuildAndSaveManualDailyReportTests(unittest.TestCase):
    """Тести ручного формування та збереження щоденного звіту.
    Tests for manual daily report generation and saving.
    """

    def test_build_and_save_manual_daily_report_creates_user_file_and_internal_copy(self) -> None:
        """Перевіряє створення зовнішнього .docx та внутрішньої копії звіту.
        Checks that both the user .docx file and the internal copy are created.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)
            target_path = Path(temporary_directory) / "export" / "daily-report.docx"
            save_result = build_and_save_manual_daily_report(
                context.database_path,
                target_path,
                access_role=AccessRole.INSPECTOR,
            )
            self.assertTrue(save_result.user_file_path.exists())
            self.assertTrue(save_result.internal_copy_path.exists())
            self.assertEqual(save_result.user_file_path.suffix.lower(), ".docx")
            with zipfile.ZipFile(save_result.user_file_path) as archive:
                self.assertIn("word/document.xml", archive.namelist())
            shut_down_logging()

    def test_manual_report_file_creation_writes_audit(self) -> None:
        """Перевіряє запис audit-події після ручного формування звіту.
        Checks that an audit event is written after manual report creation.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)
            target_path = Path(temporary_directory) / "export" / "daily-report.docx"
            save_result = build_and_save_manual_daily_report(
                context.database_path,
                target_path,
                access_role=AccessRole.INSPECTOR,
            )
            audit_entries = load_audit_log_entries(context.database_path, limit=40)
            self.assertTrue(
                any(
                    entry.event_type == "report.file_created"
                    and str(save_result.user_file_path) in entry.description_text
                    for entry in audit_entries
                )
            )
            shut_down_logging()


if __name__ == "__main__":
    unittest.main()
