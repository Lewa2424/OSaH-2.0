from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget

from osah.domain.entities.contractor_readiness_status import ContractorReadinessStatus
from osah.ui.qt.design.tokens import COLOR, RADIUS, SPACING


class ContractorsFilterBar(QWidget):
    """Фільтри реєстру підрядників.
    Contractors registry filters.
    """

    filters_changed = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("contractorsFilterBar")
        self.setStyleSheet(
            f"""
            QWidget#contractorsFilterBar {{
                background: rgba(255, 255, 255, 0.95);
                border: 1px solid #D8E3EE;
                border-radius: {RADIUS['xxl']}px;
            }}
            QWidget#contractorsFilterBar QLineEdit,
            QWidget#contractorsFilterBar QComboBox {{
                min-height: 40px;
                background: #FFFFFF;
                color: {COLOR['text_primary']};
                border: 1px solid #C8D6E5;
                border-radius: {RADIUS['lg']}px;
                padding: 0 14px;
                font-size: 14px;
                font-weight: 600;
            }}
            QWidget#contractorsFilterBar QLineEdit:focus,
            QWidget#contractorsFilterBar QComboBox:focus {{
                border: 1px solid {COLOR['accent']};
                background: #FCFEFF;
            }}
            QWidget#contractorsFilterBar QComboBox::drop-down {{
                width: 32px;
                border: none;
                background: transparent;
            }}
            QWidget#contractorsFilterBar QPushButton {{
                min-height: 40px;
                padding: 0 18px;
                border-radius: {RADIUS['lg']}px;
                font-size: 14px;
                font-weight: 800;
            }}
            QWidget#contractorsFilterBar QLabel#filterState {{
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

        self._search = QLineEdit()
        self._search.setPlaceholderText("Пошук: організація, контакт, телефон, email, робота")
        self._search.textChanged.connect(lambda _text: self.filters_changed.emit())
        layout.addWidget(self._search, stretch=2)

        self._status = QComboBox()
        self._status.addItem("Усі статуси", "")
        self._status.addItem("Готовий", ContractorReadinessStatus.READY.value)
        self._status.addItem("Є зауваження", ContractorReadinessStatus.WARNING.value)
        self._status.addItem("Не готовий", ContractorReadinessStatus.BLOCKED.value)
        self._status.addItem("Завершений", ContractorReadinessStatus.FINISHED.value)
        self._status.addItem("Архівний", ContractorReadinessStatus.ARCHIVED.value)
        self._status.currentIndexChanged.connect(lambda _index: self.filters_changed.emit())
        layout.addWidget(self._status)

        reset_button = QPushButton("Скинути")
        reset_button.setProperty("variant", "secondary")
        reset_button.clicked.connect(self._reset)
        layout.addWidget(reset_button)

        self._active_label = QLabel("Фільтри не активні")
        self._active_label.setObjectName("filterState")
        layout.addWidget(self._active_label)
        layout.addStretch(1)

    def _reset(self) -> None:
        """Скидає активні фільтри підрядників.
        Resets active contractor filters.
        """

        self._search.clear()
        self._status.setCurrentIndex(0)
        self._update_indicator()
        self.filters_changed.emit()

    def values(self) -> dict[str, str]:
        """Повертає поточні значення фільтрів.
        Returns current filters state.
        """

        values = {
            "search": self._search.text().strip().lower(),
            "status": str(self._status.currentData() or ""),
        }
        self._update_indicator()
        return values

    def _update_indicator(self) -> None:
        """Оновлює індикатор кількості активних фільтрів.
        Updates active-filters count label.
        """

        count = int(bool(self._search.text().strip())) + int(bool(self._status.currentData()))
        self._active_label.setText("Фільтри не активні" if count == 0 else f"Активних фільтрів: {count}")
