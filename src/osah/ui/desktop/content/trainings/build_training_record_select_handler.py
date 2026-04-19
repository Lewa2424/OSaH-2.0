from collections.abc import Callable
from tkinter import StringVar

from osah.domain.entities.training_record import TrainingRecord
from osah.domain.services.format_training_type_label import format_training_type_label
from osah.ui.desktop.content.trainings.extract_training_record_id import extract_training_record_id


# ###### ПОБУДОВА ОБРОБНИКА ВИБОРУ ЗАПИСУ ІНСТРУКТАЖУ / ПОСТРОЕНИЕ ОБРАБОТЧИКА ВЫБОРА ЗАПИСИ ИНСТРУКТАЖА ######
def build_training_record_select_handler(
    selected_record_var: StringVar,
    record_lookup: dict[int, TrainingRecord],
    employee_option_lookup: dict[str, str],
    selected_employee_var: StringVar,
    training_type_var: StringVar,
    event_date_var: StringVar,
    next_control_date_var: StringVar,
    conducted_by_var: StringVar,
    note_var: StringVar,
) -> Callable[[object], None]:
    """Повертає обробник, який заповнює форму редагування даними запису.
    Возвращает обработчик, который заполняет форму редактирования данными записи.
    """

    # ###### ВИБІР ЗАПИСУ ІНСТРУКТАЖУ / ВЫБОР ЗАПИСИ ИНСТРУКТАЖА ######
    def select_training_record(_: object) -> None:
        """Заповнює форму редагування значеннями вибраного запису.
        Заполняет форму редактирования значениями выбранной записи.
        """

        record_id = extract_training_record_id(selected_record_var)
        if record_id is None or record_id not in record_lookup:
            return

        training_record = record_lookup[record_id]
        selected_employee_var.set(
            employee_option_lookup.get(
                training_record.employee_personnel_number,
                training_record.employee_personnel_number,
            )
        )
        training_type_var.set(format_training_type_label(training_record.training_type))
        event_date_var.set(training_record.event_date)
        next_control_date_var.set(training_record.next_control_date)
        conducted_by_var.set(training_record.conducted_by)
        note_var.set(training_record.note_text)

    return select_training_record
