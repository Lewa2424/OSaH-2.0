from dataclasses import dataclass


@dataclass(slots=True)
class ServiceResetRequest:
    """Дані для сервісного скидання пароля по установці.
    Данные для сервисного сброса пароля по установке.
    """

    installation_id: str
    request_counter: int
