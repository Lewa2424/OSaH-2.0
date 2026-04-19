from collections.abc import Callable
from pathlib import Path
from tkinter import BooleanVar, StringVar, messagebox

from osah.application.services.save_mail_settings import save_mail_settings
from osah.domain.entities.mail_settings import MailSettings


# ###### ПОБУДОВА ОБРОБНИКА ЗБЕРЕЖЕННЯ ПОШТОВИХ НАЛАШТУВАНЬ / ПОСТРОЕНИЕ ОБРАБОТЧИКА СОХРАНЕНИЯ ПОЧТОВЫХ НАСТРОЕК ######
def build_save_mail_settings_handler(
    database_path: Path,
    daily_report_enabled_var: BooleanVar,
    smtp_host_var: StringVar,
    smtp_port_var: StringVar,
    smtp_username_var: StringVar,
    smtp_password_var: StringVar,
    sender_email_var: StringVar,
    recipient_email_var: StringVar,
    use_tls_var: BooleanVar,
    last_sent_date: str,
    on_success: Callable[[], None],
) -> Callable[[], None]:
    """Повертає обробник збереження SMTP-настроек і параметрів щоденного звіту.
    Возвращает обработчик сохранения SMTP-настроек и параметров ежедневного отчёта.
    """

    # ###### ЗБЕРЕЖЕННЯ ПОШТОВИХ НАЛАШТУВАНЬ / СОХРАНЕНИЕ ПОЧТОВЫХ НАСТРОЕК ######
    def save_current_mail_settings() -> None:
        """Зберігає поточні поштові налаштування з форми.
        Сохраняет текущие почтовые настройки из формы.
        """

        try:
            smtp_port = int(smtp_port_var.get().strip() or "0")
        except ValueError:
            messagebox.showerror("Помилка налаштувань", "SMTP-порт має бути цілим числом.")
            return
        if smtp_port < 0:
            messagebox.showerror("Помилка налаштувань", "SMTP-порт не може бути від'ємним.")
            return

        save_mail_settings(
            database_path,
            MailSettings(
                daily_report_enabled=daily_report_enabled_var.get(),
                smtp_host=smtp_host_var.get().strip(),
                smtp_port=smtp_port,
                smtp_username=smtp_username_var.get().strip(),
                smtp_password=smtp_password_var.get(),
                sender_email=sender_email_var.get().strip(),
                recipient_email=recipient_email_var.get().strip(),
                use_tls=use_tls_var.get(),
                last_sent_date=last_sent_date,
            ),
        )
        messagebox.showinfo("Налаштування збережено", "Поштові параметри успішно оновлено.")
        on_success()

    return save_current_mail_settings
