import unittest

from osah.domain.services.list_work_permit_kind_options import list_work_permit_kind_options


class ListWorkPermitKindOptionsTests(unittest.TestCase):
    """Тести каталогу типових видів нарядів-допусків.
    Tests for the catalog of typical work-permit kinds.
    """

    def test_list_work_permit_kind_options_returns_unique_catalog(self) -> None:
        """Перевіряє, що каталог містить унікальні ключі та базові універсальні шаблони.
        Verifies that the catalog contains unique keys and basic universal templates.
        """

        options = list_work_permit_kind_options()

        self.assertGreaterEqual(len(options), 5)
        self.assertEqual(len({option.key for option in options}), len(options))
        self.assertIn("Вогневі роботи", {option.label for option in options})
        self.assertIn("Інший вид робіт", {option.label for option in options})


if __name__ == "__main__":
    unittest.main()
