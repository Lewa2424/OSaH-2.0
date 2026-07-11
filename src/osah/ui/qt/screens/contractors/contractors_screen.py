from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSplitter, QVBoxLayout, QWidget

from osah.application.services.delete_contractor_record import delete_contractor_record
from osah.application.services.load_contractor_workspace import load_contractor_workspace
from osah.application.services.save_contractor_record import save_contractor_record
from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.contractor_workspace_row import ContractorWorkspaceRow
from osah.domain.services.build_contractor_workspace_rows import build_contractor_workspace_rows
from osah.ui.qt.components.form_feedback_label import FormFeedbackLabel
from osah.ui.qt.components.install_ambient_background import install_ambient_background
from osah.ui.qt.components.read_only_banner import ReadOnlyBanner
from osah.ui.qt.components.screen_states import EmptyStateWidget
from osah.ui.qt.components.scrollable_table_frame import ScrollableTableFrame
from osah.ui.qt.components.section_header import SectionHeader
from osah.ui.qt.design.tokens import SPACING
from osah.ui.qt.screens.contractors.contractor_details_pane import ContractorDetailsPane
from osah.ui.qt.screens.contractors.contractors_filter_bar import ContractorsFilterBar
from osah.ui.qt.screens.contractors.contractors_registry_table import ContractorsRegistryTable


class ContractorsScreen(QWidget):
    """Легкий екран підрядників з контролем готовності до робіт.
    Lightweight contractors screen with work-readiness control.
    """

    def __init__(self, database_path: Path, access_role: AccessRole) -> None:
        super().__init__()
        self._database_path = database_path
        self._access_role = access_role
        self._workspace = load_contractor_workspace(database_path)
        self._rows = build_contractor_workspace_rows(self._workspace.records)
        self._read_only = access_role != AccessRole.INSPECTOR

        install_ambient_background(
            self,
            "contractorsScreen",
            theme="contractors",
            extra_rules="""
            QWidget#contractorsScreen QSplitter::handle { background: transparent; }
            QWidget#contractorsScreen QSplitter::handle:horizontal { width: 10px; }
            """,
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["xl"], SPACING["lg"], SPACING["xl"], SPACING["lg"])
        layout.setSpacing(SPACING["lg"])

        self._section_header = SectionHeader(
            "Підрядники",
            "Легкий контроль підрядників: хто працює, чи готові люди до робіт і де є проблеми з допуском.",
        )
        layout.addWidget(self._section_header)

        if self._read_only:
            layout.addWidget(ReadOnlyBanner("Режим тільки перегляду: редагування підрядників вимкнено."))

        self._feedback = FormFeedbackLabel()
        layout.addWidget(self._feedback)

        self._filter_bar = ContractorsFilterBar()
        self._filter_bar.filters_changed.connect(self._apply_filters)
        layout.addWidget(self._filter_bar)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        self._table = ContractorsRegistryTable()
        self._table.row_selected.connect(self._show_row)
        splitter.addWidget(ScrollableTableFrame(self._table))
        self._details = ContractorDetailsPane(read_only=self._read_only)
        self._details.save_requested.connect(self._save_record)
        self._details.delete_requested.connect(self._delete_record)
        splitter.addWidget(self._details)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 0)
        layout.addWidget(splitter, stretch=1)

        self._empty_state = EmptyStateWidget()
        layout.addWidget(self._empty_state)
        self._apply_filters()

    def _reload_workspace(self) -> None:
        """Перезавантажує робочий простір підрядників зі сховища.
        Reloads contractors workspace from storage.
        """

        self._workspace = load_contractor_workspace(self._database_path)
        self._rows = build_contractor_workspace_rows(self._workspace.records)
        self._apply_filters()

    def _apply_filters(self) -> None:
        """Застосовує активні фільтри до реєстру підрядників.
        Applies active filters to contractors registry.
        """

        values = self._filter_bar.values()
        rows = tuple(row for row in self._rows if _contractor_matches(row, values))
        self._table.set_rows(rows)
        self._table.select_first()
        if rows:
            self._empty_state.hide()
            return
        self._empty_state.show_state(
            "Реєстр підрядників порожній.",
            "Створіть перший запис або змініть активні фільтри.",
        )

    def _show_row(self, row: ContractorWorkspaceRow) -> None:
        """Показує вибраний рядок підрядника в картці праворуч.
        Shows selected contractor row in the right-side details card.
        """

        self._details.show_record(row.record, row.readiness)

    def _save_record(self, record) -> None:
        """Зберігає картку підрядника через application service.
        Persists contractor card through application service.
        """

        if self._read_only:
            self._feedback.show_error("Режим read-only: редагування недоступне.")
            return
        try:
            saved = save_contractor_record(
                self._database_path,
                record,
                access_role=self._access_role,
            )
        except Exception as error:  # noqa: BLE001
            self._feedback.show_error(f"Не вдалося зберегти підрядника: {error}")
            return
        self._feedback.show_success(f"Запис '{saved.company_name}' збережено.")
        self._reload_workspace()

    def _delete_record(self, contractor_id: str) -> None:
        """Видаляє картку підрядника через application service.
        Deletes contractor card through application service.
        """

        if self._read_only:
            self._feedback.show_error("Режим read-only: видалення недоступне.")
            return
        try:
            delete_contractor_record(
                self._database_path,
                contractor_id,
                access_role=self._access_role,
            )
        except Exception as error:  # noqa: BLE001
            self._feedback.show_error(f"Не вдалося видалити підрядника: {error}")
            return
        self._feedback.show_success("Запис підрядника видалено.")
        self._details._reset_form()
        self._reload_workspace()


def _contractor_matches(row: ContractorWorkspaceRow, values: dict[str, str]) -> bool:
    """Перевіряє, чи відповідає підрядник активним фільтрам.
    Checks whether contractor row matches active filters.
    """

    if values["status"] and row.readiness.status.value != values["status"]:
        return False
    if values["search"]:
        haystack = " ".join(
            (
                row.record.company_name,
                row.record.contact_person,
                row.record.contact_phone,
                row.record.contact_email,
                row.record.enterprise_supervisor,
                row.record.work_scope_text,
                row.record.note_text,
                " ".join(worker.full_name for worker in row.record.workers),
            )
        ).lower()
        if values["search"] not in haystack:
            return False
    return True
