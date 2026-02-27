"""Tests for the calculator module."""

import pytest
from src.calculator import add, subtract, multiply, divide, power, factorial, is_prime


class TestAdd:
    def test_positive_numbers(self):
        assert add(2, 3) == 5

    def test_negative_numbers(self):
        assert add(-1, -1) == -2

    def test_zero(self):
        assert add(0, 5) == 5

    def test_floats(self):
        assert add(0.1, 0.2) == pytest.approx(0.3)


class TestSubtract:
    def test_basic(self):
        assert subtract(10, 4) == 6

    def test_negative_result(self):
        assert subtract(3, 7) == -4

    def test_zero_result(self):
        assert subtract(5, 5) == 0


class TestMultiply:
    def test_positive(self):
        assert multiply(3, 4) == 12

    def test_by_zero(self):
        assert multiply(99, 0) == 0

    def test_negative_times_negative(self):
        assert multiply(-3, -4) == 12

    def test_negative_times_positive(self):
        assert multiply(-3, 4) == -12


class TestDivide:
    def test_basic(self):
        assert divide(10, 2) == 5.0

    def test_fractional_result(self):
        assert divide(7, 2) == pytest.approx(3.5)

    def test_negative_dividend(self):
        assert divide(-10, 2) == -5.0

    def test_divide_by_zero_raises(self):
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            divide(5, 0)

    def test_divide_zero_by_nonzero(self):
        assert divide(0, 5) == 0.0


class TestPower:
    def test_positive_exponent(self):
        assert power(2, 3) == 8

    def test_zero_exponent(self):
        assert power(99, 0) == 1

    def test_negative_exponent(self):
        assert power(2, -1) == pytest.approx(0.5)

    def test_exponent_one(self):
        assert power(7, 1) == 7

    def test_float_exponent_raises(self):
        with pytest.raises(TypeError, match="Exponent must be an integer"):
            power(2, 1.5)

    def test_string_exponent_raises(self):
        with pytest.raises(TypeError):
            power(2, "3")


class TestFactorial:
    def test_zero(self):
        assert factorial(0) == 1

    def test_one(self):
        assert factorial(1) == 1

    def test_small(self):
        assert factorial(5) == 120

    def test_large(self):
        assert factorial(20) == 2432902008176640000

    def test_negative_raises(self):
        with pytest.raises(ValueError, match="non-negative integer"):
            factorial(-1)

    def test_float_raises(self):
        with pytest.raises(ValueError, match="non-negative integer"):
            factorial(1.5)

    def test_string_raises(self):
        with pytest.raises(ValueError):
            factorial("5")


class TestIsPrime:
    @pytest.mark.parametrize("n,expected", [
        (0, False),
        (1, False),
        (2, True),
        (3, True),
        (4, False),
        (7, True),
        (9, False),
        (11, True),
        (13, True),
        (97, True),
        (100, False),
    ])
    def test_primality(self, n, expected):
        assert is_prime(n) is expected

    def test_negative_number(self):
        assert is_prime(-7) is False

    def test_large_prime(self):
        assert is_prime(7919) is True

    def test_large_composite(self):
        assert is_prime(7920) is False
