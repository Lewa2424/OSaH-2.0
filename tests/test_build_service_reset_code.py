import unittest

from osah.domain.services.security.build_service_reset_code import build_service_reset_code
from osah.domain.services.security.generate_service_reset_secret import generate_service_reset_secret


class BuildServiceResetCodeTests(unittest.TestCase):
    """Тести побудови сервісного коду скидання."""

    def test_build_service_reset_code_is_stable_for_same_inputs(self) -> None:
        secret = generate_service_reset_secret()
        first_code = build_service_reset_code("install-001", 3, secret)
        second_code = build_service_reset_code("install-001", 3, secret)
        self.assertEqual(first_code, second_code)

    def test_build_service_reset_code_changes_with_counter(self) -> None:
        secret = generate_service_reset_secret()
        first_code = build_service_reset_code("install-001", 3, secret)
        second_code = build_service_reset_code("install-001", 4, secret)
        self.assertNotEqual(first_code, second_code)


if __name__ == "__main__":
    unittest.main()
