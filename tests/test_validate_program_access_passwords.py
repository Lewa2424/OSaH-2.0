import unittest

from osah.domain.services.security.validate_program_access_passwords import validate_program_access_passwords


class ValidateProgramAccessPasswordsTests(unittest.TestCase):
    """Тести вимог до паролів доступу."""

    def test_rejects_password_shorter_than_eight_characters(self) -> None:
        with self.assertRaises(ValueError):
            validate_program_access_passwords("short", "manager-654321")

    def test_rejects_equal_role_passwords(self) -> None:
        with self.assertRaises(ValueError):
            validate_program_access_passwords("same-password", "same-password")


if __name__ == "__main__":
    unittest.main()
