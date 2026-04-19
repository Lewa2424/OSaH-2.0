"""Переиспользуемые константы стилей для CTk-виджетов контентной области.
Reusable CTk widget style constants for the content area.
"""

from osah.ui.desktop.security.apply_desktop_theme import STYLE_TOKENS

# Карточка (glassmorphism, белая с обводкой)
CARD = {
    "fg_color": STYLE_TOKENS["surface_background"],
    "corner_radius": 20,
    "border_width": 1,
    "border_color": STYLE_TOKENS["border_color"],
}

# Вставлений фрейм (slighly grey inset)
INSET = {
    "fg_color": STYLE_TOKENS["shell_surface"],
    "corner_radius": 12,
    "border_width": 1,
    "border_color": STYLE_TOKENS["border_color"],
}

# Прозорий фрейм
TRANSPARENT = {
    "fg_color": "transparent",
    "corner_radius": 0,
}

# Accent-кнопка (синя)
BTN = {
    "corner_radius": 15,
    "fg_color": STYLE_TOKENS["accent_background"],
    "hover_color": STYLE_TOKENS["accent_hover_background"],
    "text_color": "#FFFFFF",
    "border_width": 1,
    "border_color": STYLE_TOKENS["accent_hover_background"],
    "font": ("Segoe UI", 11, "bold"),
    "height": 38,
}

# Вторинна кнопка (біла з обводкою)
BTN_SEC = {
    "corner_radius": 15,
    "fg_color": STYLE_TOKENS["surface_background"],
    "hover_color": "#F3F4F6",
    "text_color": STYLE_TOKENS["strong_text"],
    "border_width": 1,
    "border_color": STYLE_TOKENS["border_color"],
    "font": ("Segoe UI", 11),
    "height": 38,
}

# Поле введення
ENTRY = {
    "corner_radius": 12,
    "border_color": STYLE_TOKENS["border_color"],
    "fg_color": STYLE_TOKENS["surface_background"],
    "text_color": STYLE_TOKENS["strong_text"],
    "font": ("Segoe UI", 11),
    "height": 38,
}

# Комбобокс (залишається ttk, але стилізований через ttk.Style)
# Чекбокс / Радіокнопка
CHECKBOX = {
    "font": ("Segoe UI", 11),
    "text_color": STYLE_TOKENS["strong_text"],
    "fg_color": STYLE_TOKENS["accent_background"],
    "hover_color": STYLE_TOKENS["accent_hover_background"],
    "checkmark_color": "#FFFFFF",
}

RADIO = {
    "font": ("Segoe UI", 11),
    "text_color": STYLE_TOKENS["strong_text"],
    "fg_color": STYLE_TOKENS["accent_background"],
    "hover_color": STYLE_TOKENS["accent_hover_background"],
}

# Типові CTkLabel-стилі
def label_title(parent, text: str, wraplength: int = 0):
    """CTkLabel у стилі заголовка панелі."""
    import customtkinter as ctk
    kwargs = {"wraplength": wraplength, "justify": "left"} if wraplength else {}
    return ctk.CTkLabel(
        parent,
        text=text,
        text_color=STYLE_TOKENS["strong_text"],
        font=("Segoe UI", 13, "bold"),
        anchor="w",
        **kwargs,
    )


def label_body(parent, text: str, wraplength: int = 0):
    """CTkLabel у стилі тексту панелі."""
    import customtkinter as ctk
    kwargs = {"wraplength": wraplength, "justify": "left"} if wraplength else {}
    return ctk.CTkLabel(
        parent,
        text=text,
        text_color="#374151",
        font=("Segoe UI", 10),
        anchor="w",
        **kwargs,
    )


def label_muted(parent, text: str, wraplength: int = 0):
    """CTkLabel у стилі приглушеного підпису."""
    import customtkinter as ctk
    kwargs = {"wraplength": wraplength, "justify": "left"} if wraplength else {}
    return ctk.CTkLabel(
        parent,
        text=text,
        text_color=STYLE_TOKENS["muted_text"],
        font=("Segoe UI", 10, "bold"),
        anchor="w",
        **kwargs,
    )


def label_content_title(parent, text: str):
    """CTkLabel для великого заголовка екрана."""
    import customtkinter as ctk
    return ctk.CTkLabel(
        parent,
        text=text,
        text_color=STYLE_TOKENS["strong_text"],
        font=("Segoe UI", 24, "bold"),
        anchor="w",
    )


def label_metric_value(parent, text: str):
    """CTkLabel для великого числового значення метрики."""
    import customtkinter as ctk
    return ctk.CTkLabel(
        parent,
        text=text,
        text_color=STYLE_TOKENS["strong_text"],
        font=("Segoe UI", 28, "bold"),
        anchor="w",
    )


def pill_label(parent, text: str, fg_color: str, text_color: str = "#FFFFFF"):
    """CTkLabel у стилі pill-мітки зі статусом."""
    import customtkinter as ctk
    return ctk.CTkLabel(
        parent,
        text=text,
        fg_color=fg_color,
        text_color=text_color,
        corner_radius=10,
        font=("Segoe UI", 9, "bold"),
        padx=10,
        pady=3,
        anchor="w",
    )
