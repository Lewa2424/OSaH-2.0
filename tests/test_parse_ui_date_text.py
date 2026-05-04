import unittest
from datetime import date

from osah.domain.services.parse_ui_date_text import parse_ui_date_text


class ParseUiDateTextTests(unittest.TestCase):
    """Тести розбору дат з UI.
    Tests for parsing UI date values.
    """

    def test_accepts_single_digit_day_and_month(self) -> None:
        """Приймає дату без ведучих нулів.
        Accepts date without leading zeros.
        """

        self.assertEqual(parse_ui_date_text("1.2.2025"), date(2025, 2, 1))

    def test_accepts_two_digit_year(self) -> None:
        """Приймає дворічний запис року.
        Accepts a two-digit year notation.
        """

        self.assertEqual(parse_ui_date_text("1.2.25"), date(2025, 2, 1))

    def test_accepts_commas_as_separator(self) -> None:
        """Приймає кому як роздільник дати.
        Accepts commas as date separators.
        """

        self.assertEqual(parse_ui_date_text("1,2,2025"), date(2025, 2, 1))


if __name__ == "__main__":
    unittest.main()
