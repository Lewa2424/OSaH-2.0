from PySide6.QtWidgets import QMessageBox, QWidget

from osah.ui.qt.components.app_dialog import AppDialogAction, AppDialogIcon, show_app_dialog


_ICON_BY_MESSAGE_BOX: dict[QMessageBox.Icon, AppDialogIcon] = {
    QMessageBox.Icon.Information: AppDialogIcon.INFO,
    QMessageBox.Icon.Warning: AppDialogIcon.WARNING,
    QMessageBox.Icon.Critical: AppDialogIcon.CRITICAL,
    QMessageBox.Icon.Question: AppDialogIcon.QUESTION,
}


# ###### ПОКАЗ СТИЛІЗОВАНОГО MESSAGE BOX / ПОКАЗ СТИЛИЗОВАННОГО MESSAGE BOX ######
def show_styled_message_box(
    parent: QWidget | None,
    title_text: str,
    body_text: str,
    icon: QMessageBox.Icon,
    standard_buttons: QMessageBox.StandardButton,
    default_button: QMessageBox.StandardButton,
) -> QMessageBox.StandardButton:
    """Показує компактний діалог у стилі ClearWork та повертає натиснуту стандартну кнопку.
    Shows a compact ClearWork-styled dialog and returns the clicked standard button.
    """

    dialog_icon = _ICON_BY_MESSAGE_BOX.get(icon, AppDialogIcon.INFO)
    has_yes = bool(standard_buttons & QMessageBox.StandardButton.Yes)
    has_no = bool(standard_buttons & QMessageBox.StandardButton.No)

    if has_yes and has_no:
        selected_action_id = show_app_dialog(
            parent,
            window_title=title_text,
            message=body_text,
            icon=dialog_icon,
            actions=(
                AppDialogAction("no", "Скасувати", "secondary"),
                AppDialogAction("yes", "Так", "accent"),
            ),
            default_action_id="yes" if default_button == QMessageBox.StandardButton.Yes else "no",
        )
        return (
            QMessageBox.StandardButton.Yes
            if selected_action_id == "yes"
            else QMessageBox.StandardButton.No
        )

    show_app_dialog(
        parent,
        window_title=title_text,
        message=body_text,
        icon=dialog_icon,
        actions=(AppDialogAction("ok", "OK", "accent"),),
        default_action_id="ok",
    )
    return QMessageBox.StandardButton.Ok
