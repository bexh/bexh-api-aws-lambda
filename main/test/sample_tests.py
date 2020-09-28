import pytest
from main.src.utils import datetime_to_display_format
from datetime import datetime


@pytest.fixture
def thing():
    return 20


def fixture_example_test(thing):
    assert thing == 20


@pytest.mark.parametrize("year, month, day, hour, minute, expected_output", [
    (2020, 9, 27, 22, 10, "Sunday, September 27th, 10:10 PM"),
    (2020, 9, 1, 10, 00, "Tuesday, September 1st, 10:00 AM")
])
def test_datetime_to_display_format(year, month, day, hour, minute, expected_output):
    dt = datetime(year=year, month=month, day=day, hour=hour, minute=minute)
    output = datetime_to_display_format(dt)
    assert output == expected_output


