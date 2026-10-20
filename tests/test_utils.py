import pytest

from otto.utils.date import format_date_range
from otto.utils.esn import EsnColor
from otto.utils.string import slugify_string


@pytest.mark.parametrize(
    ("from_iso", "to_iso", "expected"),
    [
        (None, None, ""),
        ("2026-03-01", None, "1st of March"),
        (None, "2026-03-02", "2nd of March"),
        ("2026-03-03", "2026-03-03", "3rd of March"),
        ("2026-03-04", "2026-03-11", "4th - 11th of March"),
        ("2026-03-30", "2026-04-02", "30th of March - 2nd of April"),
    ],
)
def test_format_date_range(from_iso, to_iso, expected):
    assert format_date_range(from_iso, to_iso) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("Hello World", "hello-world"),
        ("  Trip to Lofoten!  ", "trip-to-lofoten"),
        ("Café -- Night", "cafe-night"),
        ("_-dashes-_", "dashes"),
        (42, "42"),
    ],
)
def test_slugify_string(value, expected):
    assert slugify_string(value) == expected


def test_slugify_string_keeps_unicode_when_allowed():
    assert slugify_string("Kåre Øl", allow_unicode=True) == "kåre-øl"


def test_esn_color_values():
    assert EsnColor.CYAN.display_name() == "Cyan"
    assert EsnColor.CYAN.hex() == "#00AEEF"
    assert EsnColor.CYAN.rgb() == (0, 174, 239)


def test_esn_color_from_display_name():
    assert EsnColor.from_display_name("Dark Blue") is EsnColor.DARK_BLUE
    assert EsnColor.from_display_name("Purple") is None
