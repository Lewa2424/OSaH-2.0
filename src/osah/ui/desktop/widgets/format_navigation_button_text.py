from osah.domain.entities.app_section import AppSection


# ###### ФОРМАТУВАННЯ ТЕКСТУ КНОПКИ НАВІГАЦІЇ / ФОРМАТИРОВАНИЕ ТЕКСТА КНОПКИ НАВИГАЦИИ ######
def format_navigation_button_text(section: AppSection) -> str:
    """Повертає чистий текст кнопки навігації без зайвої міжсимвольної розрядки.
    Возвращает чистый текст кнопки навигации без лишней межсимвольной разрядки.
    """

    return section.value
