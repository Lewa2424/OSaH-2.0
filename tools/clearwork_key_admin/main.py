import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

PROJECT_ROOT = Path(__file__).resolve().parent
SOURCE_ROOT = PROJECT_ROOT.parents[1] / "src"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ui.main_window import KeyAdminMainWindow


def main() -> None:
    """Запускає mini-програму обліку ключів установки ClearWork.
    Launches the ClearWork setup key admin mini-application.
    """

    application = QApplication(sys.argv)
    window = KeyAdminMainWindow(PROJECT_ROOT)
    window.show()
    sys.exit(application.exec())


if __name__ == "__main__":
    main()
