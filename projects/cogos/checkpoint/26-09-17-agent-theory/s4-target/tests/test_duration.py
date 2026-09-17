"""Behavioural tests for parse_duration (criterion for the parse-duration item)."""

import pytest

from duration import parse_duration


@pytest.mark.parametrize(
    "text, expected",
    [
        ("1h30m", 5400),
        ("45s", 45),
        ("2h", 7200),
        ("1h30m10s", 5410),
        ("90m", 5400),
        ("1m", 60),
        ("0s", 0),
    ],
)
def test_parse_duration_valid(text, expected):
    assert parse_duration(text) == expected


@pytest.mark.parametrize(
    "text",
    [
        "",
        "1h30",
        "h",
        "1x",
        "1h 30m",
        "abc",
        "1h30m!",
        "-5s",
        "1.5h",
    ],
)
def test_parse_duration_malformed_raises_value_error(text):
    with pytest.raises(ValueError):
        parse_duration(text)
