from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QSplitter, QVBoxLayout, QWidget

from osah.application.services.load_contractor_workspace import load_contractor_workspace
from osah.application.services.save_contractor_record import save_contractor_record
from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.contractor_record import ContractorRecord
from osah.domain.entities.contractor_workspace import ContractorWorkspace
from osah.ui.qt.components.form_feedback_label import FormFeedbackLabel
from osah.ui.qt.design.tokens import COLOR, SPACING
from osah.ui.qt.screens.contractors.contractor_details_pane import ContractorDetailsPane
from osah.ui.qt.screens.contractors.contractors_filter_bar import ContractorsFilterBar
from osah.ui.qt.screens.contractors.contractors_registry_table import ContractorsRegistryTable


class ContractorsScreen(QWidget):
    """Staged contractors screen with registry and editable card."""

    def __init__(self, database_path: Path, access_role: AccessRole) -> None:
        super().__init__()
        self._database_path = database_path
        self._access_role = access_role
        self._workspace = load_contractor_workspace(database_path)
        self._read_only = access_role != AccessRole.INSPECTOR

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["xl"], SPACING["lg"], SPACING["xl"], SPACING["lg"])
        layout.setSpacing(SPACING["lg"])

        title = QLabel("Підрядники")
        title.setStyleSheet("font-size: 22px; font-weight: 900;")
        layout.addWidget(title)
        subtitle = QLabel("Базовий реєстр підрядників: контакти, статус активності, робочі примітки та staged-контур допусків.")
        subtitle.setStyleSheet(f"color: {COLOR['text_secondary']};")
        layout.addWidget(subtitle)

        self._feedback = FormFeedbackLabel()
        layout.addWidget(self._feedback)

        self._filter_bar = ContractorsFilterBar()
        self._filter_bar.filters_changed.connect(self._apply_filters)
        layout.addWidget(self._filter_bar)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        self._table = ContractorsRegistryTable()
        self._table.row_selected.connect(self._show_record)
        splitter.addWidget(self._table)
        self._details = ContractorDetailsPane(read_only=self._read_only)
        self._details.save_requested.connect(self._save_record)
        splitter.addWidget(self._details)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 0)
        layout.addWidget(splitter, stretch=1)

        self._empty_state = QLabel("")
        self._empty_state.setStyleSheet(f"color: {COLOR['text_muted']};")
        layout.addWidget(self._empty_state)
        self._apply_filters()

    # ###### ОНОВЛЕННЯ ДАНИХ ПІДРЯДНИКІВ / RELOAD CONTRACTORS DATA ######
    def _reload_workspace(self) -> None:
        """Reloads contractors workspace from storage."""

        self._workspace = load_contractor_workspace(self._database_path)
        self._apply_filters()

    # ###### ЗАСТОСУВАННЯ ФІЛЬТРІВ ПІДРЯДНИКІВ / APPLY CONTRACTORS FILTERS ######
    def _apply_filters(self) -> None:
        """Applies active filters to contractors registry."""

        values = self._filter_bar.values()
        rows = tuple(record for record in self._workspace.records if _contractor_matches(record, values))
        self._table.set_rows(rows)
        self._table.select_first()
        self._empty_state.setText(
            "" if rows else "Реєстр порожній. Створіть перший запис підрядника або змініть активні фільтри."
        )

    # ###### ПОКАЗ КАРТКИ ПІДРЯДНИКА / SHOW CONTRACTOR CARD ######
    def _show_record(self, record: ContractorRecord) -> None:
        """Shows selected contractor in details pane."""

        self._details.show_record(record)

    # ###### ЗБЕРЕЖЕННЯ КАРТКИ ПІДРЯДНИКА / SAVE CONTRACTOR CARD ######
    def _save_record(self, record: ContractorRecord) -> None:
        """Persists contractor card through application service."""

        if self._read_only:
            self._feedback.show_error("Режим read-only: редагування недоступне.")
            return
        try:
            saved = save_contractor_record(self._database_path, record)
        except Exception as error:  # noqa: BLE001
            self._feedback.show_error(f"Не вдалося зберегти підрядника: {error}")
            return
        self._feedback.show_success(f"Запис '{saved.company_name}' збережено.")
        self._reload_workspace()


# ###### ВІДПОВІДНІСТЬ ПІДРЯДНИКА ФІЛЬТРАМ / MATCH CONTRACTOR TO FILTERS ######
def _contractor_matches(record: ContractorRecord, values: dict[str, str]) -> bool:
    """Checks whether contractor record matches active filters."""

    if values["status"] and record.activity_status != values["status"]:
        return False
    if values["search"]:
        haystack = " ".join(
            (
                record.company_name,
                record.contact_person,
                record.contact_phone,
                record.contact_email,
                record.note_text,
            )
        ).lower()
        if values["search"] not in haystack:
            return False
    return True
