from pathlib import Path

from osah.domain.services.setup_key.build_setup_key_document import build_setup_key_document
from osah.domain.services.setup_key.build_setup_key_payload import SetupKeyKind, build_setup_key_payload
from osah.domain.services.setup_key.setup_key_paste_token import encode_setup_key_paste_token


# ###### ГЕНЕРАЦІЯ КЛЮЧА УСТАНОВКИ / GENERATE SETUP KEY ######
def generate_setup_key_for_customer(
    *,
    customer: str,
    installation_id: str,
    key_kind: SetupKeyKind,
    private_key_path: Path,
) -> str:
    """Генерує підписаний paste-токен ключа установки для клієнта.
    Generates a signed setup key paste token for a customer.
    """

    payload = build_setup_key_payload(
        customer=customer,
        installation_id=installation_id,
        key_kind=key_kind,
    )
    document = build_setup_key_document(payload, private_key_path)
    return encode_setup_key_paste_token(document)
