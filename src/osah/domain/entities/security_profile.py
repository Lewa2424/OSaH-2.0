from dataclasses import dataclass


@dataclass(slots=True)
class SecurityProfile:
    """Поточний профіль безпеки локальної установки.
    Текущий профиль безопасности локальной установки.
    """

    installation_id: str
    is_configured: bool
    failed_attempt_count: int
    locked_until_text: str
    service_request_counter: int
    recovery_file_path: str
    recovery_created_at_text: str
    is_setup_key_activated: bool
    setup_key_customer: str
    setup_key_activated_at_text: str
