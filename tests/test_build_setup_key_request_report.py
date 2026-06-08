import tempfile
import unittest
from pathlib import Path

from osah.application.services.security.save_setup_key_request_report import save_setup_key_request_report
from osah.domain.services.setup_key.build_setup_key_request_report import (
    SetupKeyRequestReportInput,
    build_setup_key_request_report,
)


class BuildSetupKeyRequestReportTests(unittest.TestCase):
    """Тести текстового запиту на ключ установки.
    Tests for the setup key request text file.
    """

    def test_report_contains_installation_id_and_support_contacts(self) -> None:
        report_text = build_setup_key_request_report(
            SetupKeyRequestReportInput(
                installation_id="OSAH-ABCD-12-34",
                enterprise_name="ТОВ Тест",
                contact_person="Іваненко І.І.",
                contact_details="test@example.com",
            )
        )

        self.assertIn("OSAH-ABCD-12-34", report_text)
        self.assertIn("ТОВ Тест", report_text)
        self.assertIn("alexeyovch26@gmail.com", report_text)
        self.assertIn("+380954553545", report_text)
        self.assertIn("data\\", report_text)

    def test_save_setup_key_request_report_writes_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_path = Path(temporary_directory) / "request.txt"
            save_setup_key_request_report(
                output_path,
                SetupKeyRequestReportInput(
                    installation_id="OSAH-ABCD-12-34",
                    enterprise_name="ТОВ Тест",
                    contact_person="Іваненко І.І.",
                    contact_details="+380000000000",
                ),
            )
            self.assertTrue(output_path.exists())
            self.assertIn("ЗАПИТ НА КЛЮЧ", output_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
