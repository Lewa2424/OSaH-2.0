from PySide6.QtWidgets import QLabel

from osah.ui.qt.design.tokens import COLOR


class UnifiedStatusBadge(QLabel):
    """Unified status badge with text+color semantics."""

    _STATUS_STYLE = {
        "critical": ("Критично", COLOR["critical_subtle"], COLOR["critical"]),
        "warning": ("Увага", COLOR["warning_subtle"], COLOR["warning"]),
        "normal": ("Норма", COLOR["success_subtle"], COLOR["success"]),
        "info": ("Інфо", COLOR["accent_subtle"], COLOR["accent"]),
        "archived": ("Архів", COLOR["bg_panel"], COLOR["text_muted"]),
        "readonly": ("Тільки перегляд", COLOR["bg_panel"], COLOR["text_secondary"]),
    }

    def __init__(self, status_key: str, reason_text: str = "") -> None:
        super().__init__()
        self.setWordWrap(True)
        self.set_status(status_key, reason_text)

    # ###### ВСТАНОВЛЕННЯ СТАТУСУ БЕЙДЖА / SET BADGE STATUS ######
    def set_status(self, status_key: str, reason_text: str = "") -> None:
        """Sets badge style and text by unified status key."""

        label_text, background_color, border_color = self._STATUS_STYLE.get(
            status_key,
            ("Інфо", COLOR["accent_subtle"], COLOR["accent"]),
        )
        full_text = label_text if not reason_text.strip() else f"{label_text} — {reason_text}"
        self.setText(full_text)
        self.setStyleSheet(
            f"background: {background_color}; color: {border_color}; "
            "border-radius: 10px; border: 1px solid "
            f"{border_color}; padding: 3px 10px; font-weight: 700;"
        )
