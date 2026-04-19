"""
QtContext — глобальний контекст для Qt екранів.
Зберігає ApplicationContext та поточну роль.
"""
from dataclasses import dataclass
from PySide6.QtWidgets import QWidget

from osah.application.services.application_context import ApplicationContext
from osah.domain.entities.access_role import AccessRole
from osah.domain.entities.app_section import AppSection


@dataclass(slots=True)
class QtContext:
    """Контекст для екранів у новій Qt архітектурі.
    Context for screens in the new Qt architecture.
    """

    content_container: QWidget
    application_context: ApplicationContext
    selected_section: AppSection
    access_role: AccessRole
