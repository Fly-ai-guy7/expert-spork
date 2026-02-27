"""Tests for the calculator module.

Coverage gaps:
  - divide(): zero-division error path not tested
  - power(): TypeError for non-integer exponents not tested
  - factorial(): invalid-input error paths not tested; large values not tested
  - is_prime(): edge cases (0, 1, 2, negative numbers) not tested
"""

import pytest
from src.calculator import add, subtract, multiply, divide, power, factorial, is_prime


class TestAdd:
    def test_positive_numbers(self):
        assert add(2, 3) == 5

    def test_negative_numbers(self):
        assert add(-1, -1) == -2

    def test_zero(self):
        assert add(0, 5) == 5


class TestSubtract:
    def test_basic(self):
        assert subtract(10, 4) == 6

    def test_negative_result(self):
        assert subtract(3, 7) == -4


class TestMultiply:
    def test_positive(self):
        assert multiply(3, 4) == 12

    # Missing: multiply by zero, multiply negatives


class TestDivide:
    def test_basic(self):
        assert divide(10, 2) == 5.0

    # Missing: divide(x, 0) should raise ValueError
    # Missing: fractional results


class TestPower:
    def test_positive_exponent(self):
        assert power(2, 3) == 8

    # Missing: power(x, 0) == 1
    # Missing: power(x, negative) for negative exponents
    # Missing: TypeError when exponent is a float


class TestFactorial:
    def test_zero(self):
        assert factorial(0) == 1

    def test_small(self):
        assert factorial(5) == 120

    # Missing: factorial(-1) raises ValueError
    # Missing: factorial(1.5) raises ValueError


class TestIsPrime:
    def test_known_primes(self):
        assert is_prime(7) is True
        assert is_prime(11) is True

    def test_known_composites(self):
        assert is_prime(9) is False

    # Missing: is_prime(0), is_prime(1) -> False
    # Missing: is_prime(2) -> True (only even prime)
    # Missing: is_prime(negative) -> False
    # Missing: large prime numbers
