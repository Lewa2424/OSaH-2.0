from osah.domain.services.parse_storage_datetime_text import parse_storage_datetime_text


# ###### ПОРІВНЯННЯ ДАТ НАРЯДУ / COMPARE WORK PERMIT STORED DATETIMES ######
def work_permit_stored_datetime_texts_equal(left_text: str, right_text: str) -> bool:
    """Порівнює збережені дати наряду за значенням, а не за рядком.
    Compares persisted work-permit datetimes by value instead of raw text.
    """

    try:
        return parse_storage_datetime_text(left_text) == parse_storage_datetime_text(right_text)
    except ValueError:
        return left_text.strip() == right_text.strip()
