from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout

from osah.domain.entities.ppe_workspace_row import PpeWorkspaceRow
from osah.ui.qt.design.tokens import COLOR, RADIUS, SPACING


class PpeProblemBreakdown(QFrame):
    """Пояснення проблеми або стану вибраної позиції ЗІЗ.
    Explanation of the selected PPE item problem or state.
    """

    def __init__(self) -> None:
        super().__init__()
        self.setStyleSheet(
            f"background: {COLOR['bg_panel']}; border: 1px solid {COLOR['border_soft']};"
            f"border-radius: {RADIUS['lg']}px;"
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["md"], SPACING["md"], SPACING["md"], SPACING["md"])
        self._title = QLabel("Контекст ЗІЗ")
        self._title.setStyleSheet("font-weight: 900;")
        self._body = QLabel("Оберіть позицію, щоб побачити причину статусу.")
        self._body.setWordWrap(True)
        self._body.setStyleSheet(f"color: {COLOR['text_secondary']};")
        layout.addWidget(self._title)
        layout.addWidget(self._body)

    def set_row(self, row: PpeWorkspaceRow) -> None:
        """Оновлює пояснення за вибраною позицією ЗІЗ.
        Updates explanation from the selected PPE item.
        """

        self._title.setText(f"{row.employee_full_name} / {row.ppe_name}")
        self._body.setText(row.status_reason)
