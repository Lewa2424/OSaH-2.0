"""
Новая точка входа для Qt-застосунку з повним security flow.
Новая точка входа для Qt-приложения с полным security flow.
"""
import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QVBoxLayout, QWidget
from PySide6.QtCore import Qt

from osah.application.services.application_context import ApplicationContext
from osah.domain.entities.access_role import AccessRole
from osah.ui.qt.components.app_window import AppWindow
from osah.ui.qt.design.stylesheet import build_global_stylesheet
from osah.ui.qt.security.security_flow_controller import SecurityFlowController


class QtApplicationShell(QMainWindow):
    """
    Головне вікно Qt-застосунку, що має вітрину для security flow.
    Главное окно Qt-приложения с витриной для security flow.
    """

    def __init__(self, application_context: ApplicationContext) -> None:
        """
        Ініціалізує shell.
        Инициализирует shell.
        """
        super().__init__()
        self._app_context = application_context
        self._authenticated_window: AppWindow | None = None

        self.setWindowTitle("OSaH 2.0")
        self.setMinimumSize(1200, 700)

        # Стеколо для перемикання екранів
        self._stacked_widget = QStackedWidget()
        self.setCentralWidget(self._stacked_widget)

        # Контроллер безпеки
        self._security_controller = SecurityFlowController(
            stacked_widget=self._stacked_widget,
            application_context=application_context,
            on_authenticated=self._on_authenticated,
        )

    def _on_authenticated(self, access_role: AccessRole) -> None:
        """
        Обробник при успішній аутентифікації.
        Обработчик при успешной аутентификации.
        """
        # Очистити security screens
        while self._stacked_widget.count() > 0:
            self._stacked_widget.removeWidget(self._stacked_widget.widget(0))

        # Створити authenticated shell
        self._authenticated_window = AppWindow(self._app_context, access_role)
        self._stacked_widget.addWidget(self._authenticated_window)
        self._stacked_widget.setCurrentWidget(self._authenticated_window)


def run_qt_application(application_context: ApplicationContext) -> None:
    """
    Запускає Qt-застосунок із повним security flow.
    Запускает Qt-приложение с полным security flow.
    
    Args:
        application_context: контекст застосунку
    """
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    app.setStyleSheet(build_global_stylesheet())

    # Створити головне вікно із security flow
    shell = QtApplicationShell(application_context)
    shell.show()

    # Запуск циклу подій
    sys.exit(app.exec())
