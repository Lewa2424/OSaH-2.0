from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class RegistryEntityResolution:
    """Результат зіставлення фрагмента запиту з реєстром.
    Result of matching a query fragment against a registry.
    """

    status: str
    canonical_name: str | None = None
    candidates: tuple[str, ...] = ()
    resolved_personnel_number: str | None = None
