from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget

from osah.domain.entities.archive_entry_type import ArchiveEntryType
from osah.ui.qt.design.tokens import COLOR, RADIUS, SPACING


class ArchiveFilterBar(QWidget):
    """Filters for archive registry."""

    filters_changed = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("archiveFilterBar")
        self.setStyleSheet(
            f"""
            QWidget#archiveFilterBar {{
                background: rgba(255, 255, 255, 0.95);
                border: 1px solid #D8E3EE;
                border-radius: {RADIUS['xxl']}px;
            }}
            QWidget#archiveFilterBar QLineEdit,
            QWidget#archiveFilterBar QComboBox {{
                min-height: 40px;
                background: #FFFFFF;
                color: {COLOR['text_primary']};
                border: 1px solid #C8D6E5;
                border-radius: {RADIUS['lg']}px;
                padding: 0 14px;
                font-size: 14px;
                font-weight: 600;
            }}
            QWidget#archiveFilterBar QLineEdit:focus,
            QWidget#archiveFilterBar QComboBox:focus {{
                border: 1px solid {COLOR['accent']};
                background: #FCFEFF;
            }}
            QWidget#archiveFilterBar QComboBox::drop-down {{
                width: 32px;
                border: none;
                background: transparent;
            }}
            QWidget#archiveFilterBar QPushButton {{
                min-height: 40px;
                padding: 0 18px;
                border-radius: {RADIUS['lg']}px;
                font-size: 14px;
                font-weight: 800;
            }}
            QWidget#archiveFilterBar QLabel#filterState {{
                color: {COLOR['text_muted']};
                font-size: 13px;
                font-weight: 700;
            }}
            """
        )

        outer = QVBoxLayout(self)
        outer.setContentsMargins(SPACING["lg"], SPACING["lg"], SPACING["lg"], SPACING["lg"])
        outer.setSpacing(SPACING["sm"])

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING["sm"])
        outer.addLayout(layout)

        self._type_filter = QComboBox()
        self._type_filter.addItem("Усі типи", "")
        self._type_filter.addItem("Архівні працівники", ArchiveEntryType.EMPLOYEE.value)
        self._type_filter.addItem("Історичні наряди", ArchiveEntryType.WORK_PERMIT.value)
        self._type_filter.currentIndexChanged.connect(lambda _index: self.filters_changed.emit())
        layout.addWidget(self._type_filter)

        self._search = QLineEdit()
        self._search.setPlaceholderText("Пошук: ПІБ, номер, причина, підрозділ")
        self._search.textChanged.connect(lambda _text: self.filters_changed.emit())
        layout.addWidget(self._search, stretch=1)

        reset_button = QPushButton("Скинути")
        reset_button.setProperty("variant", "secondary")
        reset_button.clicked.connect(self._reset_filters)
        layout.addWidget(reset_button)

        self._active_label = QLabel("Фільтри не активні")
        self._active_label.setObjectName("filterState")
        layout.addWidget(self._active_label)
        layout.addStretch(1)

    def _reset_filters(self) -> None:
        """Resets archive filters to defaults."""

        self._type_filter.setCurrentIndex(0)
        self._search.clear()
        self._update_indicator()
        self.filters_changed.emit()

    def values(self) -> dict[str, str]:
        """Returns current archive filters."""

        values = {
            "entry_type": str(self._type_filter.currentData() or ""),
            "search": self._search.text().strip().lower(),
        }
        self._update_indicator()
        return values

    def _update_indicator(self) -> None:
        """Updates active filters indicator."""

        count = int(bool(self._type_filter.currentData())) + int(bool(self._search.text().strip()))
        self._active_label.setText("Фільтри не активні" if count == 0 else f"Активних фільтрів: {count}")
