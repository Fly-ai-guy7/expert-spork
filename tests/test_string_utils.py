"""Tests for string_utils — partially covered module."""

import pytest
from expert_spork.string_utils import slugify, truncate, word_count


# --- slugify (covered) ---

def test_slugify_basic():
    assert slugify("Hello World") == "hello-world"


def test_slugify_special_chars():
    assert slugify("Hello, World!") == "hello-world"


def test_slugify_type_error():
    with pytest.raises(TypeError):
        slugify(123)


# --- truncate (partially covered) ---

def test_truncate_no_truncation_needed():
    assert truncate("Hi", 10) == "Hi"


def test_truncate_exact_length():
    assert truncate("Hello", 5) == "Hello"


def test_truncate_with_default_suffix():
    assert truncate("Hello World", 8) == "Hello..."


# Missing: test_truncate_custom_suffix
# Missing: test_truncate_suffix_too_long (ValueError)
# Missing: test_truncate_type_error


# --- word_count (minimal coverage) ---

def test_word_count_basic():
    result = word_count("the cat and the dog")
    assert result["the"] == 2
    assert result["cat"] == 1


# Missing: test_word_count_empty_string
# Missing: test_word_count_punctuation
# Missing: test_word_count_type_error
# Missing: test_word_count_case_insensitivity


# NOTE: camel_to_snake, snake_to_camel, is_palindrome have NO tests at all.
