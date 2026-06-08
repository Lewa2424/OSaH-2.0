from dataclasses import dataclass

from osah.infrastructure.config.support_contacts import SUPPORT_EMAIL, SUPPORT_PHONE


@dataclass(slots=True)
class SetupKeyRequestReportInput:
    """Дані для текстового запиту на ключ установки.
    Data for the setup key request text file.
    """

    installation_id: str
    enterprise_name: str
    contact_person: str
    contact_details: str


# ###### ТЕКСТ ЗАПИТУ НА КЛЮЧ / SETUP KEY REQUEST REPORT TEXT ######
def build_setup_key_request_report(report_input: SetupKeyRequestReportInput) -> str:
    """Формує текстовий файл-запит, який клієнт надсилає розробнику.
    Builds the text request file that the customer sends to the developer.
    """

    return (
        "ЗАПИТ НА КЛЮЧ УСТАНОВКИ CLEARWORK\n"
        "================================\n\n"
        "ДАНІ УСТАНОВКИ\n"
        f"ID установки: {report_input.installation_id.strip()}\n"
        f"Підприємство: {report_input.enterprise_name.strip()}\n"
        f"Контактна особа: {report_input.contact_person.strip()}\n"
        f"Контакти для відповіді: {report_input.contact_details.strip()}\n\n"
        "КУДИ НАДІСЛАТИ\n"
        f"Email: {SUPPORT_EMAIL}\n"
        f"Телефон: {SUPPORT_PHONE}\n\n"
        "НАВІЩО ЦЕ ПОТРІБНО\n"
        "Ключ установки прив'язується до ID установки у локальній базі ClearWork.\n"
        "Після отримання ключа вставте рядок CW-... на екрані активації програми.\n\n"
        "ВАЖЛИВО\n"
        "ID установки зберігається у папці data\\ поруч із програмою, а не в «залізі» комп'ютера.\n"
        "Якщо видалити ClearWork разом із папкою data\\, з'явиться новий ID установки,\n"
        "і старий ключ уже не підійде. З міркувань безпеки потрібна нова генерація ключа.\n"
        "Якщо переустановлюєте програму на тому ж ПК — не видаляйте папку data\\.\n"
    )
