import unittest

from osah.domain.services.build_default_smtp_settings import build_default_smtp_settings


class BuildDefaultSmtpSettingsTests(unittest.TestCase):
    """Тести базового автоформування SMTP-параметрів.
    Tests for baseline automatic SMTP settings generation.
    """

    def test_builds_generic_smtp_values_from_sender_email(self) -> None:
        """Перевіряє формування базових SMTP-значень з адреси відправника.
        Checks building baseline SMTP values from sender email.
        """

        smtp_host, smtp_port, smtp_username, use_tls = build_default_smtp_settings("user@example.com")

        self.assertEqual(smtp_host, "smtp.example.com")
        self.assertEqual(smtp_port, 587)
        self.assertEqual(smtp_username, "user@example.com")
        self.assertTrue(use_tls)

    def test_returns_empty_host_when_email_is_invalid(self) -> None:
        """Перевіряє безпечний результат для невалідної адреси.
        Checks safe result for invalid address.
        """

        smtp_host, smtp_port, smtp_username, use_tls = build_default_smtp_settings("invalid-email")

        self.assertEqual(smtp_host, "")
        self.assertEqual(smtp_port, 587)
        self.assertEqual(smtp_username, "")
        self.assertTrue(use_tls)


if __name__ == "__main__":
    unittest.main()
