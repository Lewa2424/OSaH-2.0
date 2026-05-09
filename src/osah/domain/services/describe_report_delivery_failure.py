def describe_report_delivery_failure(description_text: str) -> str:
    """Повертає зрозуміле пояснення причини збою поштової доставки за audit-описом.
    Returns a user-friendly explanation for mail delivery failure from audit description text.
    """

    error_code = _extract_error_code(description_text)
    if error_code == "SMTPAuthenticationError":
        return "Помилка авторизації SMTP. Перевірте адресу відправника, логін, пароль пошти та вимоги вашого поштового сервера."
    if error_code == "SMTPConnectError":
        return "Не вдалося підключитися до поштового сервера. Перевірте SMTP host, порт і доступ до мережі."
    if error_code == "SMTPServerDisconnected":
        return "Поштовий сервер розірвав з'єднання. Перевірте параметри безпеки та повторіть спробу."
    if error_code == "SMTPSenderRefused":
        return "Поштовий сервер відхилив адресу відправника. Перевірте адресу та політику вашого поштового сервера."
    if error_code == "SMTPRecipientsRefused":
        return "Поштовий сервер відхилив адресу отримувача. Перевірте список отримувачів."
    if error_code == "SMTPDataError":
        return "Поштовий сервер відхилив вміст або формат листа. Перевірте обмеження вашого поштового сервера."
    if error_code:
        return f"Поштовий сервер повернув помилку {error_code}. Перевірте параметри пошти та вимоги провайдера."
    return "Причину збою не вдалося визначити. Перевірте параметри пошти та історію подій нижче."


def _extract_error_code(description_text: str) -> str:
    """Повертає код помилки після маркера error= або порожній рядок.
    Returns the error code after the error= marker or an empty string.
    """

    marker = "error="
    if marker not in description_text:
        return ""
    value = description_text.partition(marker)[2].strip()
    return value.split(";", maxsplit=1)[0].strip()
