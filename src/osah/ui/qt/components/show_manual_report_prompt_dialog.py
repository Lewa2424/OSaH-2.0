from PySide6.QtWidgets import QWidget

from osah.ui.qt.components.app_dialog import AppDialogAction, AppDialogIcon, show_app_dialog

_RESULT_BUILD = "build"
_RESULT_SKIP = "skip"
_RESULT_LATER = "later"


# ###### ДІАЛОГ НАГАДУВАННЯ ПРО ЩОДЕННИЙ ЗВІТ / SHOW MANUAL REPORT PROMPT DIALOG ######
def show_manual_report_prompt_dialog(parent: QWidget | None) -> str:
    """Показує стилізований діалог нагадування про щоденний звіт і повертає вибір користувача.
    Shows a styled daily report reminder dialog and returns the user's choice.
    """

    return show_app_dialog(
        parent,
        window_title="Щоденний звіт",
        message="Настав час сформувати щоденний звіт.",
        detail="Сформувати файл звіту зараз?",
        icon=AppDialogIcon.QUESTION,
        actions=(
            AppDialogAction(_RESULT_BUILD, "Так, сформувати", "accent"),
            AppDialogAction(_RESULT_SKIP, "Пропустити сьогодні", "secondary"),
            AppDialogAction(_RESULT_LATER, "Нагадати пізніше", "secondary"),
        ),
        default_action_id=_RESULT_BUILD,
        button_layout="stacked",
    )
