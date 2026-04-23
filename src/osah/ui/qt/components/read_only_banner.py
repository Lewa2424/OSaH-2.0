from PySide6.QtWidgets import QLabel


class ReadOnlyBanner(QLabel):
    """Unified read-only mode marker for manager role."""

    def __init__(self, text: str = "Режим тільки перегляду: редагування вимкнено.") -> None:
        super().__init__(text)
        self.setProperty("role", "readonly_banner")
        self.setWordWrap(True)
