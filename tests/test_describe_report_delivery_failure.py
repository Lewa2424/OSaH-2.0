import unittest

from osah.domain.services.describe_report_delivery_failure import describe_report_delivery_failure


class DescribeReportDeliveryFailureTests(unittest.TestCase):
    """Тести пояснення причин збою поштової доставки.
    Tests for user-facing explanations of mail delivery failures.
    """

    def test_returns_authentication_hint_for_smtp_auth_error(self) -> None:
        """Пояснює помилку авторизації SMTP зрозумілим текстом.
        Explains SMTP authentication failures with a clear message.
        """

        message_text = describe_report_delivery_failure("fallback_copy=file.eml;error=SMTPAuthenticationError")
        self.assertIn("Помилка авторизації SMTP", message_text)

    def test_returns_generic_message_for_unknown_error(self) -> None:
        """Пояснює невідомий код без падіння парсингу.
        Explains unknown codes without breaking parsing.
        """

        message_text = describe_report_delivery_failure("fallback_copy=file.eml;error=CustomError")
        self.assertIn("CustomError", message_text)

    def test_returns_fallback_message_when_error_marker_missing(self) -> None:
        """Повертає загальне пояснення, якщо error-маркер відсутній.
        Returns a fallback message when the error marker is missing.
        """

        message_text = describe_report_delivery_failure("fallback_copy=file.eml")
        self.assertIn("Причину збою", message_text)


if __name__ == "__main__":
    unittest.main()
