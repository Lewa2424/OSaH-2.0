from dataclasses import dataclass


@dataclass(slots=True)
class MailSettings:
    """Налаштування поштового контуру для щоденного звіту.
    Настройки почтового контура для ежедневного отчёта.
    """

    daily_report_enabled: bool
    smtp_host: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    sender_email: str
    recipient_email: str
    use_tls: bool
    last_sent_date: str
    daily_report_time: str = "08:00"
