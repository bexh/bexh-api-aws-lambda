import pytest


@pytest.fixture
def thing():
    return 20


def test_1(thing):
    assert thing == 20


@pytest.mark.parametrize("param1, param2", [
    ("foo", 1),
    ("bar", 2)
])
def test_2(param1, param2):
    assert param1 in ["foo", "bar"]
    assert param2 in [1, 2]


