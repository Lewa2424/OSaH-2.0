from datetime import date, datetime

import pytest

from osah.domain.services.format_ui_date import format_ui_date
from osah.domain.services.format_ui_datetime import format_ui_datetime
from osah.domain.services.parse_ui_date_text import parse_ui_date_text
from osah.domain.services.parse_ui_datetime_text import parse_ui_datetime_text


@pytest.mark.parametrize(
    ("raw_text", "expected_date"),
    (
        ("01.01.2026", date(2026, 1, 1)),
        ("1.1.2026", date(2026, 1, 1)),
        ("1.1.26", date(2026, 1, 1)),
        ("01,01,2026", date(2026, 1, 1)),
        ("1,1,26", date(2026, 1, 1)),
    ),
)
def test_parse_ui_date_text_accepts_allowed_formats(raw_text: str, expected_date: date) -> None:
    assert parse_ui_date_text(raw_text) == expected_date


@pytest.mark.parametrize(
    "raw_text",
    (
        "2026-01-01",
        "2026.01.01",
        "01/01/2026",
        "01-01-2026",
        "01:01:2026",
        "01.01",
        "abc",
    ),
)
def test_parse_ui_date_text_rejects_disallowed_formats(raw_text: str) -> None:
    with pytest.raises(ValueError):
        parse_ui_date_text(raw_text)


@pytest.mark.parametrize(
    ("raw_text", "expected_datetime"),
    (
        ("01.01.2026 08:00", datetime(2026, 1, 1, 8, 0)),
        ("1.1.2026 8:00", datetime(2026, 1, 1, 8, 0)),
        ("1.1.26 8:05", datetime(2026, 1, 1, 8, 5)),
        ("01,01,2026 08:00", datetime(2026, 1, 1, 8, 0)),
    ),
)
def test_parse_ui_datetime_text_accepts_allowed_formats(raw_text: str, expected_datetime: datetime) -> None:
    assert parse_ui_datetime_text(raw_text) == expected_datetime


@pytest.mark.parametrize(
    "raw_text",
    (
        "2026-01-01 08:00",
        "01/01/2026 08:00",
        "01-01-2026 08:00",
        "01.01.2026",
        "01.01.2026 8",
        "text",
    ),
)
def test_parse_ui_datetime_text_rejects_disallowed_formats(raw_text: str) -> None:
    with pytest.raises(ValueError):
        parse_ui_datetime_text(raw_text)


def test_format_ui_date_formats_storage_iso_date() -> None:
    assert format_ui_date("2026-01-01") == "01.01.2026"


@pytest.mark.parametrize(
    ("raw_text", "expected_text"),
    (
        ("2026-01-01 08:00", "01.01.2026 08:00"),
        ("2026-01-01 08:00:00", "01.01.2026 08:00"),
    ),
)
def test_format_ui_datetime_formats_storage_iso_datetime(raw_text: str, expected_text: str) -> None:
    assert format_ui_datetime(raw_text) == expected_text
