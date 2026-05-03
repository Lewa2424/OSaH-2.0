from osah.domain.entities.training_next_control_basis import TrainingNextControlBasis


# ###### ФОРМАТ ОСНОВАНИЯ КОНТРОЛЯ ИНСТРУКТАЖА / FORMAT TRAINING CONTROL BASIS ######
def format_training_next_control_basis_label(
    next_control_basis: TrainingNextControlBasis,
) -> str:
    """Возвращает понятную подпись основания расчёта следующего контроля.
    Returns a readable label for the next control calculation basis.
    """

    labels = {
        TrainingNextControlBasis.MANUAL: "Ручна дата",
        TrainingNextControlBasis.REQUIRES_PRIMARY_AFTER_INTRODUCTORY: "Потрібен первинний після вступного",
        TrainingNextControlBasis.INTRODUCTORY_PRIMARY_NOT_REQUIRED: "Вступний зафіксовано без вимоги первинного",
        TrainingNextControlBasis.CALCULATED_AFTER_PRIMARY_3M: "Первинний: +3 місяці",
        TrainingNextControlBasis.CALCULATED_AFTER_PRIMARY_6M: "Первинний: +6 місяців",
        TrainingNextControlBasis.CALCULATED_AFTER_REPEATED_3M: "Повторний: +3 місяці",
        TrainingNextControlBasis.CALCULATED_AFTER_REPEATED_6M: "Повторний: +6 місяців",
        TrainingNextControlBasis.RECALCULATED_AFTER_UNSCHEDULED_3M: "Позаплановий перенос: +3 місяці",
        TrainingNextControlBasis.RECALCULATED_AFTER_UNSCHEDULED_6M: "Позаплановий перенос: +6 місяців",
        TrainingNextControlBasis.RECALCULATED_AFTER_TARGETED_3M: "Цільовий перенос: +3 місяці",
        TrainingNextControlBasis.RECALCULATED_AFTER_TARGETED_6M: "Цільовий перенос: +6 місяців",
        TrainingNextControlBasis.DOES_NOT_CHANGE_REPEATED_CONTROL: "Не переносить повторний контроль",
    }
    return labels[next_control_basis]
