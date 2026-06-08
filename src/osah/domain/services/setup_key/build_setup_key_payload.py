from datetime import date
from typing import Any, Literal

SetupKeyKind = Literal["initial", "rebind"]


# ###### ПОБУДОВА PAYLOAD КЛЮЧА УСТАНОВКИ / BUILD SETUP KEY PAYLOAD ######
def build_setup_key_payload(
    *,
    customer: str,
    installation_id: str,
    key_kind: SetupKeyKind = "initial",
    issued_at: str | None = None,
) -> dict[str, Any]:
    """Формує payload підписаного ключа установки ClearWork.
    Builds the payload for a signed ClearWork setup key.
    """

    return {
        "product": "ClearWork",
        "customer": customer.strip(),
        "installation_id": installation_id.strip(),
        "key_kind": key_kind,
        "issued_at": issued_at or date.today().isoformat(),
    }
