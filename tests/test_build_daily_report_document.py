import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from osah.application.services.build_daily_report_document import build_daily_report_document
from osah.application.services.initialize_application import initialize_application
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class BuildDailyReportDocumentTests(unittest.TestCase):
    """Тести побудови щоденного звіту.
    Тесты построения ежедневного отчёта.
    """

    # ###### ПЕРЕВІРКА ПОБУДОВИ ДОКУМЕНТА ЩОДЕННОГО ЗВІТУ / ПРОВЕРКА ПОСТРОЕНИЯ ДОКУМЕНТА ЕЖЕДНЕВНОГО ОТЧЁТА ######
    def test_build_daily_report_document_returns_subject_and_body(self) -> None:
        """Перевіряє, що документ звіту містить тему та ключові рядки тіла.
        Проверяет, что документ отчёта содержит тему и ключевые строки тела.
        """

        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)

            daily_report_document = build_daily_report_document(
                context.database_path,
                created_at=datetime(2026, 4, 10, 9, 30),
            )

            self.assertIn("2026-04-10", daily_report_document.subject_text)
            self.assertIn("Працівників у системі", daily_report_document.body_text)
            self.assertIn("Фокус дня", daily_report_document.body_text)
            shut_down_logging()


if __name__ == "__main__":
    unittest.main()
