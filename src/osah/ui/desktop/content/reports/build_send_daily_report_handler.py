from collections.abc import Callable
from pathlib import Path
from tkinter import messagebox

from osah.application.services.send_daily_report_email import send_daily_report_email


# ###### ПОБУДОВА ОБРОБНИКА НАДСИЛАННЯ ЩОДЕННОГО ЗВІТУ / ПОСТРОЕНИЕ ОБРАБОТЧИКА ОТПРАВКИ ЕЖЕДНЕВНОГО ОТЧЁТА ######
def build_send_daily_report_handler(database_path: Path, on_success: Callable[[], None]) -> Callable[[], None]:
    """Повертає обробник ручного надсилання щоденного звіту.
    Возвращает обработчик ручной отправки ежедневного отчёта.
    """

    # ###### НАДСИЛАННЯ ЩОДЕННОГО ЗВІТУ / ОТПРАВКА ЕЖЕДНЕВНОГО ОТЧЁТА ######
    def send_daily_report_now() -> None:
        """Пробує відправити щоденний звіт і показує результат користувачу.
        Пытается отправить ежедневный отчёт и показывает результат пользователю.
        """

        try:
            report_copy_path, failed_email_copy_path = send_daily_report_email(database_path)
        except ValueError as error:
            messagebox.showerror("Помилка надсилання", str(error))
            return

        if failed_email_copy_path is None:
            messagebox.showinfo(
                "Звіт надіслано",
                f"Щоденний звіт надіслано успішно. Копію збережено: {report_copy_path}",
            )
        else:
            messagebox.showwarning(
                "Надсилання не виконано",
                f"Автоматична відправка не вдалася. Копію звіту збережено: {report_copy_path}\n"
                f"Лист для ручної відправки: {failed_email_copy_path}",
            )
        on_success()

    return send_daily_report_now
