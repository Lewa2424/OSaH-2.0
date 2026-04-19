"""
Точка входу для нового Qt-інтерфейсу.
Entry point for the new Qt UI layer.
"""
import sys

from PySide6.QtWidgets import QApplication

from osah.application.services.application_context import ApplicationContext
from osah.domain.entities.access_role import AccessRole
from osah.ui.qt.components.app_window import AppWindow
from osah.ui.qt.design.stylesheet import build_global_stylesheet


# ###### ЗАПУСК QT-ЗАСТОСУНКУ / ЗАПУСК QT-ПРИЛОЖЕНИЯ ######
def run_qt_application(application_context: ApplicationContext) -> None:
    """Ініціалізує QApplication, застосовує стилі і відкриває головне вікно.
    Initializes QApplication, applies stylesheet and opens the main window.
    """
    
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    app.setStyleSheet(build_global_stylesheet())

    # Тимчасово: пропускаємо логін, використовуємо роль INSPECTOR для дев-режиму
    # В майбутньому тут буде завантажуватись реальний профіль і відображатись екран входу
    dummy_role = AccessRole.INSPECTOR

    window = AppWindow(application_context, dummy_role)
    window.show()

    # Запуск циклу подій
    sys.exit(app.exec())
