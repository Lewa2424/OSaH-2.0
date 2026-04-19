from pathlib import Path
import sys


# ###### ЗАПУСК ІЗ КОРЕНЯ / ЗАПУСК ИЗ КОРНЯ ######
def run_from_root() -> None:
    """Запускає застосунок із кореневої директорії проєкту.
    Запускает приложение из корневой директории проекта.
    """

    project_root = Path(__file__).resolve().parent
    source_root = project_root / "src"
    if str(source_root) not in sys.path:
        sys.path.insert(0, str(source_root))

    from osah.main import main

    main()


if __name__ == "__main__":
    run_from_root()
