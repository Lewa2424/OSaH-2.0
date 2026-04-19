from osah.domain.entities.app_section import AppSection
from osah.ui.desktop.desktop_context import DesktopContext


# ###### ПЕРЕМИКАННЯ РОЗДІЛУ / ПЕРЕКЛЮЧЕНИЕ РАЗДЕЛА ######
def handle_section_selection(desktop_context: DesktopContext, section: AppSection) -> None:
    """Оновлює активний розділ і перемальовує shell з новим станом навігації.
    Обновляет активный раздел и перерисовывает shell с новым состоянием навигации.
    """

    from osah.ui.desktop.security.render_authenticated_shell import render_authenticated_shell

    desktop_context.selected_section = section
    render_authenticated_shell(
        desktop_context.root,
        desktop_context.application_context,
        desktop_context.access_role,
        selected_section=section,
    )
