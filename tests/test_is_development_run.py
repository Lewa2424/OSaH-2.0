import sys
import unittest
from unittest.mock import patch

from osah.infrastructure.config.is_development_run import is_development_run


class IsDevelopmentRunTests(unittest.TestCase):
    """Тести визначення запуску з вихідного коду."""

    def test_returns_true_when_not_frozen(self) -> None:
        with patch.object(sys, "frozen", False, create=True):
            self.assertTrue(is_development_run())

    def test_returns_false_for_frozen_build(self) -> None:
        with patch.object(sys, "frozen", True, create=True):
            self.assertFalse(is_development_run())


if __name__ == "__main__":
    unittest.main()
