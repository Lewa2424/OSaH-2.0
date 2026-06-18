from enum import StrEnum


class AiCommandTrack(StrEnum):
    """Головний рельс AI-команди після розбору фрази.
    Top-level AI command track after phrase analysis.
    """

    READ = "read"
    NAV = "nav"
    WRITE = "write"
