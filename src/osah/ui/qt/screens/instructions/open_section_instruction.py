from PySide6.QtWidgets import QWidget

from osah.domain.entities.app_section import AppSection
from osah.ui.qt.screens.instructions.instruction_registry import get_instruction_entry
from osah.ui.qt.screens.instructions.section_instruction_dialog import SectionInstructionDialog


def open_section_instruction(section: AppSection, parent: QWidget | None = None) -> None:
    """Відкриває модальну інструкцію для обраного розділу.
    Opens the modal instruction screen for the selected app section.
    """

    entry = get_instruction_entry(section)
    if entry is None:
        return
    dialog = SectionInstructionDialog(
        entry.title,
        entry.subtitle,
        entry.build_content(),
        parent=parent,
    )
    dialog.exec()
