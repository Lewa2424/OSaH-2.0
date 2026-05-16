import tempfile
import unittest
from pathlib import Path

from osah.application.services.create_work_permit_record import create_work_permit_record
from osah.application.services.initialize_application import initialize_application
from osah.application.services.suggest_followup_work_permit_number import suggest_followup_work_permit_number
from osah.infrastructure.config.application_paths import build_application_paths
from osah.infrastructure.logging.shutdown_logging import shut_down_logging


class SuggestFollowupWorkPermitNumberTests(unittest.TestCase):
    """Тести підбору номера для нового наряду на основі поточного.
    Tests for suggesting a new permit number based on the current one.
    """

    def test_suggest_followup_work_permit_number_returns_first_free_suffix(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            application_paths = build_application_paths(Path(temporary_directory))
            context = initialize_application(application_paths)
            create_work_permit_record(
                context.database_path,
                "ND-BASE-001",
                "Вогневі роботи",
                "Дільниця А",
                "2099-04-10 08:00",
                "2099-04-20 18:00",
                "Майстер",
                "",
                "",
                "",
                "Базовий наряд",
            )
            create_work_permit_record(
                context.database_path,
                "ND-BASE-001-R1",
                "Вогневі роботи",
                "Дільниця А",
                "2099-04-10 08:00",
                "2099-04-20 18:00",
                "Майстер",
                "",
                "",
                "",
                "Похідний наряд",
            )

            suggestion = suggest_followup_work_permit_number(context.database_path, "ND-BASE-001")

            self.assertEqual(suggestion, "ND-BASE-001-R2")
            shut_down_logging()


if __name__ == "__main__":
    unittest.main()
