import sys

from osah.application.services.initialize_application import initialize_application
from osah.infrastructure.config.application_paths import ApplicationPaths, build_application_paths
from osah.infrastructure.startup.install_uncaught_exception_hook import install_uncaught_exception_hook
from osah.infrastructure.startup.show_fatal_startup_error import show_fatal_startup_error
from osah.ui.qt.run_qt_application_secured import run_qt_application


# ###### ГОЛОВНА ТОЧКА ВХОДУ / ГЛАВНАЯ ТОЧКА ВХОДА ######
def main() -> None:
    """Запускає ініціалізацію та Qt-інтерфейс застосунку з повним security flow.
    Запускает инициализацию и Qt-интерфейс приложения с полным security flow.
    """

    application_paths: ApplicationPaths | None = None
    try:
        application_paths = build_application_paths()
        install_uncaught_exception_hook(application_paths.log_file_path)
        application_context = initialize_application(application_paths)
        run_qt_application(application_context)
    except Exception as error:
        log_file_path = (
            application_paths.log_file_path
            if application_paths is not None
            else build_application_paths().log_file_path
        )
        show_fatal_startup_error(log_file_path, error)
        sys.exit(1)


if __name__ == "__main__":
    main()
