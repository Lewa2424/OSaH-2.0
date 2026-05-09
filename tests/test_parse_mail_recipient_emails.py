import unittest

from osah.domain.services.parse_mail_recipient_emails import parse_mail_recipient_emails


class ParseMailRecipientEmailsTests(unittest.TestCase):
    """Тести розбору списку поштових отримувачів.
    Tests for parsing the mail recipients list.
    """

    def test_parses_semicolon_comma_and_newline_separated_addresses(self) -> None:
        """Перевіряє нормалізацію кількох адрес з різними роздільниками.
        Checks normalization of multiple addresses with different separators.
        """

        recipients = parse_mail_recipient_emails(
            "boss@example.com; lead@example.com,\nhr@example.com"
        )

        self.assertEqual(
            recipients,
            ("boss@example.com", "lead@example.com", "hr@example.com"),
        )


if __name__ == "__main__":
    unittest.main()
