from email.message import EmailMessage

from osah.domain.entities.daily_report_document import DailyReportDocument
from osah.domain.entities.mail_settings import MailSettings


# ###### ПОБУДОВА EMAIL-ПОВІДОМЛЕННЯ ЗВІТУ / ПОСТРОЕНИЕ EMAIL-СООБЩЕНИЯ ОТЧЁТА ######
def build_daily_report_email_message(
    daily_report_document: DailyReportDocument,
    mail_settings: MailSettings,
) -> EmailMessage:
    """Повертає готове email-повідомлення для відправки щоденного звіту.
    Возвращает готовое email-сообщение для отправки ежедневного отчёта.
    """

    email_message = EmailMessage()
    email_message["Subject"] = daily_report_document.subject_text
    email_message["From"] = mail_settings.sender_email.strip()
    email_message["To"] = mail_settings.recipient_email.strip()
    email_message.set_content(daily_report_document.body_text)
    return email_message
