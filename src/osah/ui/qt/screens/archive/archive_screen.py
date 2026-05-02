from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSplitter, QVBoxLayout, QWidget

from osah.application.services.load_archive_workspace import load_archive_workspace
from osah.application.services.reactivate_archived_employee import reactivate_archived_employee
from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.archive_entry import ArchiveEntry
from osah.ui.qt.components.form_feedback_label import FormFeedbackLabel
from osah.ui.qt.components.read_only_banner import ReadOnlyBanner
from osah.ui.qt.components.screen_states import EmptyStateWidget
from osah.ui.qt.components.scrollable_table_frame import ScrollableTableFrame
from osah.ui.qt.components.section_header import SectionHeader
from osah.ui.qt.design.tokens import SPACING
from osah.ui.qt.screens.archive.archive_details_pane import ArchiveDetailsPane
from osah.ui.qt.screens.archive.archive_filter_bar import ArchiveFilterBar
from osah.ui.qt.screens.archive.archive_registry_table import ArchiveRegistryTable


class ArchiveScreen(QWidget):
    """Archive screen with unified layout, filters, registry and details pane."""

    def __init__(self, database_path: Path, access_role: AccessRole) -> None:
        super().__init__()
        self._database_path = database_path
        self._access_role = access_role
        self._workspace = load_archive_workspace(database_path)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING["xl"], SPACING["lg"], SPACING["xl"], SPACING["lg"])
        layout.setSpacing(SPACING["lg"])

        self._section_header = SectionHeader(
            "Архів",
            "Окремий контур архівних працівників та історичних сутностей без змішування з активними.",
        )
        layout.addWidget(self._section_header)

        if access_role != AccessRole.INSPECTOR:
            layout.addWidget(ReadOnlyBanner("Режим тільки перегляду: реактивація недоступна."))

        self._feedback = FormFeedbackLabel()
        layout.addWidget(self._feedback)

        self._filter_bar = ArchiveFilterBar()
        self._filter_bar.filters_changed.connect(self._apply_filters)
        layout.addWidget(self._filter_bar)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        self._table = ArchiveRegistryTable()
        self._table.row_selected.connect(self._show_entry)
        splitter.addWidget(ScrollableTableFrame(self._table, snap_to_columns=True))
        self._details = ArchiveDetailsPane(allow_reactivation=access_role == AccessRole.INSPECTOR)
        self._details.reactivate_requested.connect(self._reactivate_entry)
        splitter.addWidget(self._details)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 0)
        layout.addWidget(splitter, stretch=1)

        self._empty_state = EmptyStateWidget()
        layout.addWidget(self._empty_state)
        self._apply_filters()

    # ###### ОНОВЛЕННЯ ДАНИХ АРХІВУ / RELOAD ARCHIVE DATA ######
    def _reload_workspace(self) -> None:
        """Reloads archive workspace after modifying actions."""

        self._workspace = load_archive_workspace(self._database_path)
        self._apply_filters()

    # ###### ЗАСТОСУВАННЯ ФІЛЬТРІВ АРХІВУ / APPLY ARCHIVE FILTERS ######
    def _apply_filters(self) -> None:
        """Applies archive filters to workspace entries."""

        values = self._filter_bar.values()
        rows = tuple(entry for entry in self._workspace.entries if _archive_entry_matches(entry, values))
        self._table.set_rows(rows)
        self._table.select_first()
        if rows:
            self._empty_state.hide()
            return
        self._empty_state.show_state(
            "Нічого не знайдено в архіві.",
            "Змініть фільтри або очистіть пошуковий запит.",
        )

    # ###### ПОКАЗ ДЕТАЛЕЙ ЗАПИСУ / SHOW ENTRY DETAILS ######
    def _show_entry(self, entry: ArchiveEntry) -> None:
        """Shows selected archive entry in details pane."""

        self._details.show_entry(entry)

    # ###### РЕАКТИВАЦІЯ З АРХІВУ / REACTIVATE FROM ARCHIVE ######
    def _reactivate_entry(self, entry_key: str) -> None:
        """Reactivates archived employee entry."""

        if self._access_role != AccessRole.INSPECTOR:
            self._feedback.show_error("Режим read-only: реактивація недоступна.")
            return
        if not entry_key.startswith("employee:"):
            return
        personnel_number = entry_key.split(":", maxsplit=1)[1]
        try:
            reactivate_archived_employee(self._database_path, personnel_number)
        except Exception as error:  # noqa: BLE001
            self._feedback.show_error(f"Не вдалося реактивувати запис: {error}")
            return
        self._feedback.show_success(f"Працівника {personnel_number} реактивовано.")
        self._reload_workspace()


# ###### ВІДПОВІДНІСТЬ ЗАПИСУ ФІЛЬТРАМ / MATCH ENTRY TO FILTERS ######
def _archive_entry_matches(entry: ArchiveEntry, values: dict[str, str]) -> bool:
    """Checks whether archive entry matches current filters."""

    if values["entry_type"] and entry.entry_type.value != values["entry_type"]:
        return False
    if values["search"]:
        haystack = " ".join((entry.title, entry.subtitle, entry.reason_text, entry.status_label)).lower()
        if values["search"] not in haystack:
            return False
    return True
