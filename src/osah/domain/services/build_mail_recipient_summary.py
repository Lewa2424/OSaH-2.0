from osah.domain.services.parse_mail_recipient_emails import parse_mail_recipient_emails


# ###### СТИСЛИЙ ПІДСУМОК ОТРИМУВАЧІВ / КРАТКАЯ СВОДКА ПОЛУЧАТЕЛЕЙ ######
def build_mail_recipient_summary(recipient_text: str) -> str:
    """Повертає стислий текст для показу отримувачів у статусному блоці.
    Returns a compact text for displaying recipients in the status block.
    """

    recipients = parse_mail_recipient_emails(recipient_text)
    if not recipients:
        return "не задано"
    if len(recipients) == 1:
        return recipients[0]
    return f"{recipients[0]} та ще {len(recipients) - 1}"
