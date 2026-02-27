"""Tests for Calculator — well-covered module."""

import pytest
from expert_spork import Calculator


@pytest.fixture
def calc():
    return Calculator()


def test_add(calc):
    assert calc.add(2, 3) == 5
    assert calc.add(-1, 1) == 0
    assert calc.add(0, 0) == 0


def test_subtract(calc):
    assert calc.subtract(10, 4) == 6
    assert calc.subtract(0, 5) == -5


def test_multiply(calc):
    assert calc.multiply(3, 4) == 12
    assert calc.multiply(-2, 5) == -10
    assert calc.multiply(0, 999) == 0


def test_divide(calc):
    assert calc.divide(10, 2) == 5.0
    assert calc.divide(7, 2) == 3.5


def test_divide_by_zero(calc):
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        calc.divide(5, 0)


def test_history_recorded(calc):
    calc.add(1, 2)
    calc.multiply(3, 4)
    assert len(calc.history) == 2
    assert calc.history[0]["op"] == "add"
    assert calc.history[1]["op"] == "multiply"


def test_last_result(calc):
    assert calc.last_result() is None
    calc.add(4, 5)
    assert calc.last_result() == 9


def test_clear_history(calc):
    calc.add(1, 1)
    calc.clear_history()
    assert calc.history == []
    assert calc.last_result() is None
