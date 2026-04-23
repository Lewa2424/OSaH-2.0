from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from osah.domain.entities.work_permit_workspace_row import WorkPermitWorkspaceRow
from osah.ui.qt.design.tokens import COLOR, SPACING


class PermitParticipantsPanel(QWidget):
    """Панель учасників і конфліктів наряду.
    Panel with work permit participants and conflicts.
    """

    def __init__(self) -> None:
        super().__init__()
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(SPACING["xs"])

    # ###### ПОКАЗ УЧАСНИКІВ / SHOW PARTICIPANTS ######
    def set_row(self, row: WorkPermitWorkspaceRow | None) -> None:
        """Показує учасників і причини конфліктів вибраного наряду.
        Shows participants and conflict reasons for the selected work permit.
        """

        while self._layout.count():
            item = self._layout.takeAt(0)
            if widget := item.widget():
                widget.deleteLater()
        if row is None:
            self._layout.addWidget(_label("Оберіть наряд для перегляду учасників.", COLOR["text_muted"]))
            return
        self._layout.addWidget(_label(f"Учасники: {row.participant_names}", COLOR["text_secondary"]))
        if row.conflict_reasons:
            for reason in row.conflict_reasons:
                self._layout.addWidget(_label(f"Критично: {reason}", COLOR["critical"]))
        else:
            self._layout.addWidget(_label("Блокуючих конфліктів учасників не знайдено.", COLOR["success"]))


# ###### ТЕКСТОВИЙ РЯДОК / LABEL ######
def _label(text: str, color: str) -> QLabel:
    """Створює службовий текстовий рядок панелі.
    Creates a helper text line for the panel.
    """

    label = QLabel(text)
    label.setWordWrap(True)
    label.setStyleSheet(f"color: {color}; font-weight: 700;")
    return label
