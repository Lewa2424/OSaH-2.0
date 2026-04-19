from osah.domain.entities.training_registry_filter import TrainingRegistryFilter
from osah.domain.entities.training_registry_row import TrainingRegistryRow


# ###### ФІЛЬТРАЦІЯ РЯДКІВ РЕЄСТРУ ІНСТРУКТАЖІВ / ФИЛЬТРАЦИЯ СТРОК РЕЕСТРА ИНСТРУКТАЖЕЙ ######
def filter_training_registry_rows(
    rows: tuple[TrainingRegistryRow, ...],
    registry_filter: TrainingRegistryFilter,
) -> tuple[TrainingRegistryRow, ...]:
    """Повертає підмножину рядків реєстру за вибраним фільтром.
    Возвращает подмножество строк реестра по выбранному фильтру.
    """

    if registry_filter == TrainingRegistryFilter.ALL:
        return rows
    return tuple(row for row in rows if row.row_filter == registry_filter)
