from osah.application.services.application_context import ApplicationContext
from osah.application.services.security.load_security_profile import load_security_profile
from osah.ui.desktop.create_root_window import create_root_window
from osah.ui.desktop.security.apply_desktop_theme import apply_desktop_theme
from osah.ui.desktop.security.render_access_reset_screen import render_access_reset_screen
from osah.ui.desktop.security.render_authenticated_shell import render_authenticated_shell
from osah.ui.desktop.security.render_initial_security_setup_screen import render_initial_security_setup_screen
from osah.ui.desktop.security.render_login_screen import render_login_screen


# ###### ЗАПУСК DESKTOP-ЗАСТОСУНКУ / ЗАПУСК DESKTOP-ПРИЛОЖЕНИЯ ######
def run_desktop_application(application_context: ApplicationContext) -> None:
    """Запускає застосунок через первинне налаштування або екран входу.
    Запускает приложение через первичную настройку или экран входа.
    """

    root = create_root_window()
    apply_desktop_theme(root)
    security_profile = load_security_profile(application_context.database_path)

    def render_login() -> None:
        """Повертає користувача на екран входу.
        Возвращает пользователя на экран входа.
        """

        render_login_screen(
            root,
            application_context,
            on_authenticated=lambda access_role: render_authenticated_shell(root, application_context, access_role),
            on_recovery_requested=render_reset_screen,
        )

    def render_reset_screen() -> None:
        """Показує екран аварійного відновлення доступу.
        Показывает экран аварийного восстановления доступа.
        """

        render_access_reset_screen(
            root,
            application_context,
            on_finished=render_login,
            on_back_to_login=render_login,
        )

    if security_profile.is_configured:
        render_login()
    else:
        render_initial_security_setup_screen(root, application_context, on_configured=render_login)
    root.mainloop()
