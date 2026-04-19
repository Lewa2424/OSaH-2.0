from dataclasses import dataclass
from tkinter import Misc, ttk

from osah.application.services.application_context import ApplicationContext
from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.app_section import AppSection


@dataclass(slots=True)
class DesktopContext:
    """Контекст desktop-інтерфейсу.
    Контекст desktop-интерфейса.
    """

    root: Misc
    content_frame: ttk.Frame
    application_context: ApplicationContext
    selected_section: AppSection
    access_role: AccessRole
