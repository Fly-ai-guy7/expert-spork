"""Tests for string_utils — full coverage."""

import pytest
from expert_spork.string_utils import (
    slugify,
    truncate,
    word_count,
    camel_to_snake,
    snake_to_camel,
    is_palindrome,
)


# ---------------------------------------------------------------------------
# slugify
# ---------------------------------------------------------------------------

def test_slugify_basic():
    assert slugify("Hello World") == "hello-world"


def test_slugify_special_chars():
    assert slugify("Hello, World!") == "hello-world"


def test_slugify_leading_trailing_spaces():
    assert slugify("  Hello World  ") == "hello-world"


def test_slugify_multiple_spaces():
    assert slugify("Hello   World") == "hello-world"


def test_slugify_unicode():
    # NKFD decomposition keeps base ASCII chars (é -> e, ö -> o)
    assert slugify("Héllo Wörld") == "hello-world"


def test_slugify_already_slug():
    assert slugify("hello-world") == "hello-world"


def test_slugify_type_error():
    with pytest.raises(TypeError):
        slugify(123)


# ---------------------------------------------------------------------------
# truncate
# ---------------------------------------------------------------------------

def test_truncate_no_truncation_needed():
    assert truncate("Hi", 10) == "Hi"


def test_truncate_exact_length():
    assert truncate("Hello", 5) == "Hello"


def test_truncate_with_default_suffix():
    assert truncate("Hello World", 8) == "Hello..."


def test_truncate_custom_suffix():
    # max_length=7, suffix len=1, so take first 6 chars + suffix
    assert truncate("Hello World", 7, suffix="…") == "Hello …"


def test_truncate_empty_suffix():
    assert truncate("Hello World", 5, suffix="") == "Hello"


def test_truncate_suffix_too_long_raises():
    with pytest.raises(ValueError):
        truncate("Hello", 2, suffix="...")


def test_truncate_type_error():
    with pytest.raises(TypeError):
        truncate(42, 5)


# ---------------------------------------------------------------------------
# word_count
# ---------------------------------------------------------------------------

def test_word_count_basic():
    result = word_count("the cat and the dog")
    assert result["the"] == 2
    assert result["cat"] == 1


def test_word_count_empty_string():
    assert word_count("") == {}


def test_word_count_punctuation_ignored():
    result = word_count("hello, hello! hello?")
    assert result["hello"] == 3


def test_word_count_case_insensitive():
    result = word_count("Apple apple APPLE")
    assert result["apple"] == 3


def test_word_count_type_error():
    with pytest.raises(TypeError):
        word_count(["not", "a", "string"])


# ---------------------------------------------------------------------------
# camel_to_snake
# ---------------------------------------------------------------------------

def test_camel_to_snake_pascal():
    assert camel_to_snake("MyClassName") == "my_class_name"


def test_camel_to_snake_camel():
    assert camel_to_snake("myVariableName") == "my_variable_name"


def test_camel_to_snake_already_snake():
    assert camel_to_snake("already_snake") == "already_snake"


def test_camel_to_snake_single_word():
    assert camel_to_snake("Word") == "word"


def test_camel_to_snake_acronym():
    # Consecutive capitals are grouped together as a word
    assert camel_to_snake("parseHTMLString") == "parse_html_string"


# ---------------------------------------------------------------------------
# snake_to_camel
# ---------------------------------------------------------------------------

def test_snake_to_camel_basic():
    assert snake_to_camel("my_variable_name") == "myVariableName"


def test_snake_to_camel_single_word():
    assert snake_to_camel("hello") == "hello"


def test_snake_to_camel_already_camel_passthrough():
    assert snake_to_camel("alreadyCamel") == "alreadyCamel"


def test_snake_to_camel_leading_underscore():
    assert snake_to_camel("_private_var") == "PrivateVar"


# ---------------------------------------------------------------------------
# is_palindrome
# ---------------------------------------------------------------------------

def test_is_palindrome_simple():
    assert is_palindrome("racecar") is True


def test_is_palindrome_with_spaces_and_caps():
    assert is_palindrome("A man a plan a canal Panama") is True


def test_is_palindrome_not_palindrome():
    assert is_palindrome("hello") is False


def test_is_palindrome_single_char():
    assert is_palindrome("a") is True


def test_is_palindrome_empty_string():
    assert is_palindrome("") is True


def test_is_palindrome_punctuation_ignored():
    assert is_palindrome("Was it a car or a cat I saw?") is True
