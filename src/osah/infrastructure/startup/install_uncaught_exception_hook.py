import sys
from pathlib import Path

from osah.infrastructure.startup.show_fatal_startup_error import show_fatal_startup_error


# ###### ГЛОБАЛЬНИЙ ПЕРЕХОПЛЮВАЧ ПОМИЛОК / GLOBAL UNCAUGHT EXCEPTION HOOK ######
def install_uncaught_exception_hook(log_file_path: Path) -> None:
    """Встановлює глобальний обробник необроблених винятків для frozen/dev запуску.
    Installs a global handler for uncaught exceptions in frozen/dev runs.
    """

    previous_hook = sys.excepthook

    def handle_uncaught_exception(
        exception_type: type[BaseException],
        exception_value: BaseException,
        exception_traceback,
    ) -> None:
        if issubclass(exception_type, KeyboardInterrupt):
            previous_hook(exception_type, exception_value, exception_traceback)
            return

        show_fatal_startup_error(log_file_path, exception_value)
        sys.exit(1)

    sys.excepthook = handle_uncaught_exception  # type: ignore[assignment]
