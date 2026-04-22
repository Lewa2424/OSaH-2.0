from osah.application.services.initialize_application import initialize_application
from osah.infrastructure.config.application_paths import build_application_paths
from osah.ui.qt.run_qt_application_secured import run_qt_application


# ###### ГОЛОВНА ТОЧКА ВХОДУ / ГЛАВНАЯ ТОЧКА ВХОДА ######
def main() -> None:
    """Запускає ініціалізацію та Qt-інтерфейс застосунку з повним security flow.
    Запускает инициализацию и Qt-интерфейс приложения с полным security flow.
    """

    application_paths = build_application_paths()
    application_context = initialize_application(application_paths)
    run_qt_application(application_context)


if __name__ == "__main__":
    main()
