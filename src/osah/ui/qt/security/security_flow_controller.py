"""
Qt security flow controller.
"""

from typing import Callable

from PySide6.QtWidgets import QStackedWidget

from osah.application.services.application_context import ApplicationContext
from osah.application.services.security.load_security_profile import load_security_profile
from osah.domain.entities.access_role import AccessRole
from osah.ui.qt.security.screens.initial_setup_screen import InitialSetupScreen
from osah.ui.qt.security.screens.login_screen import LoginScreen
from osah.ui.qt.security.screens.recovery_access_screen import RecoveryAccessScreen


class SecurityFlowController:
    """Manages transitions between login, setup and recovery screens."""

    def __init__(
        self,
        stacked_widget: QStackedWidget,
        application_context: ApplicationContext,
        on_authenticated: Callable[[AccessRole], None],
    ) -> None:
        self._stacked_widget = stacked_widget
        self._app_context = application_context
        self._on_authenticated = on_authenticated
        self._security_profile = load_security_profile(application_context.database_path)
        self._setup_screens()

    def _setup_screens(self) -> None:
        """###### ПОЧАТКОВИЙ SECURITY FLOW / INITIAL SECURITY FLOW ######"""

        if self._security_profile.is_configured:
            self._login_screen = LoginScreen(
                self._app_context,
                on_authenticated=self._on_login_authenticated,
                on_recovery_requested=self._show_recovery_screen,
            )
            self._stacked_widget.addWidget(self._login_screen)
            self._stacked_widget.setCurrentWidget(self._login_screen)
            return

        self._initial_setup_screen = InitialSetupScreen(
            self._app_context,
            on_configured=self._on_initial_setup_configured,
        )
        self._stacked_widget.addWidget(self._initial_setup_screen)
        self._stacked_widget.setCurrentWidget(self._initial_setup_screen)

    def _on_initial_setup_configured(self) -> None:
        """###### ПІСЛЯ ПЕРШОГО НАЛАШТУВАННЯ / AFTER INITIAL SETUP ######"""

        self._security_profile = load_security_profile(self._app_context.database_path)
        while self._stacked_widget.count() > 0:
            self._stacked_widget.removeWidget(self._stacked_widget.widget(0))

        self._login_screen = LoginScreen(
            self._app_context,
            on_authenticated=self._on_login_authenticated,
            on_recovery_requested=self._show_recovery_screen,
        )
        self._stacked_widget.addWidget(self._login_screen)
        self._stacked_widget.setCurrentWidget(self._login_screen)

    def _on_login_authenticated(self, access_role: AccessRole) -> None:
        """###### УСПІШНА АВТЕНТИФІКАЦІЯ / SUCCESSFUL AUTH ######"""

        self._on_authenticated(access_role)

    def _show_recovery_screen(self) -> None:
        """###### ВІДКРИТИ RECOVERY / OPEN RECOVERY ######"""

        if not hasattr(self, "_recovery_screen"):
            self._recovery_screen = RecoveryAccessScreen(
                self._app_context,
                on_finished=self._on_recovery_finished,
                on_back_to_login=self._show_login_screen,
            )
            self._stacked_widget.addWidget(self._recovery_screen)

        self._stacked_widget.setCurrentWidget(self._recovery_screen)

    def _show_login_screen(self) -> None:
        """###### ПОВЕРНЕННЯ ДО LOGIN / RETURN TO LOGIN ######"""

        if hasattr(self, "_login_screen"):
            self._stacked_widget.setCurrentWidget(self._login_screen)

    def navigate_back(self) -> None:
        """###### НАЗАД У SECURITY FLOW / BACK IN SECURITY FLOW ######"""

        if hasattr(self, "_recovery_screen") and self._stacked_widget.currentWidget() is self._recovery_screen:
            self._show_login_screen()

    def _on_recovery_finished(self) -> None:
        """###### ПІСЛЯ RECOVERY / AFTER RECOVERY ######"""

        self._show_login_screen()
