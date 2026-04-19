from dataclasses import dataclass

from osah.domain.entities.access_role import AccessRole


@dataclass(slots=True)
class AuthenticationResult:
    """Результат перевірки входу до програми.
    Результат проверки входа в программу.
    """

    is_authenticated: bool
    access_role: AccessRole | None
    message_text: str
