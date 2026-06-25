import sys

from PySide6.QtCore import QProcess
from PySide6.QtWidgets import QApplication


# ###### КОМАНДА ПЕРЕЗАПУСКУ / BUILD RESTART COMMAND ######
def build_restart_command() -> tuple[str, list[str]]:
    """Повертає програму та аргументи для перезапуску ClearWork.
    Returns the program and arguments used to relaunch ClearWork.
    """

    if getattr(sys, "frozen", False):
        return sys.executable, list(sys.argv[1:])
    return sys.executable, list(sys.argv)


# ###### ПЕРЕЗАПУСК ЗАСТОСУНКУ / REQUEST APPLICATION RESTART ######
def request_application_restart() -> bool:
    """Запускає новий процес ClearWork і завершує поточний.
    Starts a new ClearWork process and quits the current one.
    """

    application = QApplication.instance()
    if application is None:
        return False

    program, arguments = build_restart_command()
    if not QProcess.startDetached(program, arguments):
        return False

    application.quit()
    return True
