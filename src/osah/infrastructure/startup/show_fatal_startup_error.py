import ctypes
from pathlib import Path

from osah.infrastructure.config.support_contacts import SUPPORT_EMAIL, SUPPORT_PHONE
from osah.infrastructure.startup.write_fatal_startup_log import write_fatal_startup_log


# ###### ПОВІДОМЛЕННЯ ПРО ФАТАЛЬНУ ПОМИЛКУ / FATAL STARTUP ERROR MESSAGE ######
def build_fatal_startup_message(log_file_path: Path, error: BaseException) -> str:
    """Формує текст повідомлення для користувача після фатальної помилки запуску.
    Builds the user-facing message after a fatal startup error.
    """

    return (
        "ClearWork не запустився.\n\n"
        f"Причина: {error}\n\n"
        f"Деталі: {log_file_path}\n\n"
        f"Підтримка: {SUPPORT_EMAIL}\n"
        f"Телефон: {SUPPORT_PHONE}"
    )


# ###### ПОКАЗ ФАТАЛЬНОЇ ПОМИЛКИ ЗАПУСКУ / SHOW FATAL STARTUP ERROR ######
def show_fatal_startup_error(log_file_path: Path, error: BaseException) -> None:
    """Записує помилку в лог і показує користувачеві зрозуміле повідомлення.
    Logs the error and shows a clear message to the user.
    """

    write_fatal_startup_log(log_file_path, error)
    message = build_fatal_startup_message(log_file_path, error)

    try:
        from PySide6.QtWidgets import QApplication, QMessageBox

        from osah.ui.qt.branding import DISPLAY_NAME
        from osah.ui.qt.components.apply_application_visual_theme import apply_application_visual_theme
        from osah.ui.qt.components.show_styled_message_box import show_styled_message_box

        application = QApplication.instance()
        if application is None:
            application = QApplication([])
            apply_application_visual_theme(application, None)

        show_styled_message_box(
            None,
            DISPLAY_NAME,
            message,
            QMessageBox.Icon.Critical,
            QMessageBox.StandardButton.Ok,
            QMessageBox.StandardButton.Ok,
        )
        return
    except Exception:
        pass

    ctypes.windll.user32.MessageBoxW(  # type: ignore[attr-defined]
        0,
        message,
        "ClearWork",
        0x10,
    )
