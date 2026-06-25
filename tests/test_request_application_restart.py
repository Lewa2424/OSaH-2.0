import sys
import unittest
from unittest.mock import patch

from osah.ui.qt.components.request_application_restart import build_restart_command


class RequestApplicationRestartTests(unittest.TestCase):
    """Тести формування команди перезапуску.
    Tests for restart command building.
    """

    def test_build_restart_command_for_development_mode(self) -> None:
        """Повертає python і sys.argv у режимі розробки.
        Returns python and sys.argv in development mode.
        """

        with patch.object(sys, "frozen", False, create=True):
            with patch.object(sys, "executable", "python.exe"):
                with patch.object(sys, "argv", ["main.py", "--dev"]):
                    program, arguments = build_restart_command()

        self.assertEqual(program, "python.exe")
        self.assertEqual(arguments, ["main.py", "--dev"])

    def test_build_restart_command_for_frozen_build(self) -> None:
        """Повертає exe без дублювання argv[0] у зібраній версії.
        Returns the exe without duplicating argv[0] in the frozen build.
        """

        with patch.object(sys, "frozen", True, create=True):
            with patch.object(sys, "executable", "ClearWork.exe"):
                with patch.object(sys, "argv", ["ClearWork.exe", "--flag"]):
                    program, arguments = build_restart_command()

        self.assertEqual(program, "ClearWork.exe")
        self.assertEqual(arguments, ["--flag"])


if __name__ == "__main__":
    unittest.main()
