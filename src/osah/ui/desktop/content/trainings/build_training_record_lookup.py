from osah.domain.entities.training_record import TrainingRecord


# ###### ПОБУДОВА ІНДЕКСУ ЗАПИСІВ ІНСТРУКТАЖУ / ПОСТРОЕНИЕ ИНДЕКСА ЗАПИСЕЙ ИНСТРУКТАЖА ######
def build_training_record_lookup(training_records: tuple[TrainingRecord, ...]) -> dict[int, TrainingRecord]:
    """Повертає словник записів інструктажів за їх ідентифікатором.
    Возвращает словарь записей инструктажей по их идентификатору.
    """

    return {
        int(training_record.record_id): training_record
        for training_record in training_records
        if training_record.record_id is not None
    }
