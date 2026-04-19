from osah.application.services.initialize_application import initialize_application
from osah.infrastructure.config.application_paths import build_application_paths
from osah.ui.desktop.run_desktop_application import run_desktop_application


# ###### ГОЛОВНА ТОЧКА ВХОДУ / ГЛАВНАЯ ТОЧКА ВХОДА ######
def main() -> None:
    """Запускає ініціалізацію та desktop-інтерфейс застосунку.
    Запускает инициализацию и desktop-интерфейс приложения.
    """

    application_paths = build_application_paths()
    application_context = initialize_application(application_paths)
    run_desktop_application(application_context)


if __name__ == "__main__":
    main()
