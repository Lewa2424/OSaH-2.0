from email.message import EmailMessage
from pathlib import Path

from osah.domain.entities.daily_report_document import DailyReportDocument
from osah.domain.entities.mail_settings import MailSettings
from osah.domain.services.build_daily_report_email_body_text import build_daily_report_email_body_text
from osah.domain.services.parse_mail_recipient_emails import parse_mail_recipient_emails


# ###### ПОБУДОВА EMAIL-ПОВІДОМЛЕННЯ ЗВІТУ / ПОСТРОЕНИЕ EMAIL-СООБЩЕНИЯ ОТЧЁТА ######
def build_daily_report_email_message(
    daily_report_document: DailyReportDocument,
    mail_settings: MailSettings,
    report_file_path: Path,
) -> EmailMessage:
    """Повертає готове email-повідомлення для відправки щоденного звіту з вкладенням .docx.
    Returns a ready email message for sending the daily report with a .docx attachment.
    """

    email_message = EmailMessage()
    email_message["Subject"] = daily_report_document.subject_text
    email_message["From"] = mail_settings.sender_email.strip()
    email_message["To"] = ", ".join(parse_mail_recipient_emails(mail_settings.recipient_email))
    email_message.set_content(build_daily_report_email_body_text(daily_report_document.snapshot))
    email_message.add_attachment(
        report_file_path.read_bytes(),
        maintype="application",
        subtype="vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=report_file_path.name,
    )
    return email_message
