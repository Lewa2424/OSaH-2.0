"""
Qt Security Flow Controller - управління переходом між екранами безпеки.
Qt Security Flow Controller - управление переходом между экранами безопасности.
"""
from typing import Callable

from PySide6.QtWidgets import QStackedWidget, QMainWindow

from osah.application.services.application_context import ApplicationContext
from osah.application.services.security.load_security_profile import load_security_profile
from osah.domain.entities.access_role import AccessRole
from osah.ui.qt.security.screens.initial_setup_screen import InitialSetupScreen
from osah.ui.qt.security.screens.login_screen import LoginScreen
from osah.ui.qt.security.screens.recovery_access_screen import RecoveryAccessScreen


class SecurityFlowController:
    """Контролер для управління потоком безпеки в Qt-інтерфейсі.
    Контроллер для управления потоком безопасности в Qt-интерфейсе.
    """

    def __init__(
        self,
        stacked_widget: QStackedWidget,
        application_context: ApplicationContext,
        on_authenticated: Callable[[AccessRole], None],
    ) -> None:
        """
        Ініціалізує контроллер.
        Инициализирует контроллер.
        
        Args:
            stacked_widget: QStackedWidget для перемикання екранів
            application_context: контекст застосунку
            on_authenticated: callback при успішній автентифікації
        """
        self._stacked_widget = stacked_widget
        self._app_context = application_context
        self._on_authenticated = on_authenticated
        self._security_profile = load_security_profile(application_context.database_path)

        # Ініціалізуємо екрани / Инициализируем экраны
        self._setup_screens()

    def _setup_screens(self) -> None:
        """Створює і реєструє всі security screens."""
        if self._security_profile.is_configured:
            # Система налаштована, показуємо login
            self._login_screen = LoginScreen(
                self._app_context,
                on_authenticated=self._on_login_authenticated,
                on_recovery_requested=self._show_recovery_screen,
            )
            self._stacked_widget.addWidget(self._login_screen)
            self._stacked_widget.setCurrentWidget(self._login_screen)
        else:
            # Перший запуск, показуємо initial setup
            self._initial_setup_screen = InitialSetupScreen(
                self._app_context,
                on_configured=self._on_initial_setup_configured,
            )
            self._stacked_widget.addWidget(self._initial_setup_screen)
            self._stacked_widget.setCurrentWidget(self._initial_setup_screen)

    def _on_initial_setup_configured(self) -> None:
        """Обробник при завершенні першого налаштування."""
        # Перезавантажуємо профіль безпеки
        self._security_profile = load_security_profile(self._app_context.database_path)
        
        # Очищуємо попередні екрани
        while self._stacked_widget.count() > 0:
            self._stacked_widget.removeWidget(self._stacked_widget.widget(0))
        
        # Показуємо login екран
        self._login_screen = LoginScreen(
            self._app_context,
            on_authenticated=self._on_login_authenticated,
            on_recovery_requested=self._show_recovery_screen,
        )
        self._stacked_widget.addWidget(self._login_screen)
        self._stacked_widget.setCurrentWidget(self._login_screen)

    def _on_login_authenticated(self, access_role: AccessRole) -> None:
        """Обробник при успішній автентифікації."""
        self._on_authenticated(access_role)

    def _show_recovery_screen(self) -> None:
        """Показує екран відновлення доступу."""
        if not hasattr(self, "_recovery_screen"):
            self._recovery_screen = RecoveryAccessScreen(
                self._app_context,
                on_finished=self._on_recovery_finished,
                on_back_to_login=self._show_login_screen,
            )
            self._stacked_widget.addWidget(self._recovery_screen)
        
        self._stacked_widget.setCurrentWidget(self._recovery_screen)

    def _show_login_screen(self) -> None:
        """Повертає до екрана входу."""
        if hasattr(self, "_login_screen"):
            self._stacked_widget.setCurrentWidget(self._login_screen)

    def _on_recovery_finished(self) -> None:
        """Обробник при завершенні recovery."""
        self._show_login_screen()
