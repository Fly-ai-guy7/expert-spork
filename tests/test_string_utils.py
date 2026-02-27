"""Tests for string_utils module."""

import pytest
from src.string_utils import truncate, slugify, count_words, is_palindrome, mask_sensitive, camel_to_snake


class TestTruncate:
    def test_short_string_unchanged(self):
        assert truncate("hello", 10) == "hello"

    def test_long_string_truncated(self):
        assert truncate("hello world", 8) == "hello..."

    def test_exact_boundary_unchanged(self):
        # len("hi") == 2 == max_length — no truncation
        assert truncate("hi", 2) == "hi"

    def test_custom_suffix(self):
        # "…" is a single char, so text[:7-1] = "hello " + "…"
        assert truncate("hello world", 7, suffix="…") == "hello …"

    def test_empty_suffix(self):
        assert truncate("hello world", 5, suffix="") == "hello"

    def test_non_string_raises(self):
        with pytest.raises(TypeError, match="text must be a string"):
            truncate(123, 5)

    def test_zero_max_length_raises(self):
        with pytest.raises(ValueError, match="max_length must be positive"):
            truncate("hi", 0)

    def test_negative_max_length_raises(self):
        with pytest.raises(ValueError):
            truncate("hi", -1)


class TestSlugify:
    def test_basic(self):
        assert slugify("Hello World") == "hello-world"

    def test_special_chars(self):
        assert slugify("Hello, World!") == "hello-world"

    def test_leading_trailing_spaces(self):
        assert slugify("  spaces  ") == "spaces"

    def test_empty_string(self):
        assert slugify("") == ""

    def test_multiple_spaces(self):
        assert slugify("one   two") == "one-two"

    def test_hyphens_preserved(self):
        assert slugify("already-slugged") == "already-slugged"

    def test_unicode_letters_preserved(self):
        # Non-ASCII word chars are kept by \w
        result = slugify("café au lait")
        assert " " not in result
        assert result == result.lower()


class TestCountWords:
    def test_normal_sentence(self):
        assert count_words("one two three") == 3

    def test_empty_string(self):
        assert count_words("") == 0

    def test_whitespace_only(self):
        assert count_words("   ") == 0

    def test_multiple_spaces_between_words(self):
        assert count_words("one   two") == 2

    def test_single_word(self):
        assert count_words("hello") == 1

    def test_leading_trailing_whitespace(self):
        assert count_words("  hello world  ") == 2


class TestIsPalindrome:
    @pytest.mark.parametrize("text,expected", [
        ("racecar", True),
        ("hello", False),
        ("", True),
        ("a", True),
        ("Aba", True),          # case-insensitive
        ("A man a plan a canal Panama", True),  # spaces ignored
        ("race a car", False),
        ("Was it a car or a cat I saw", True),
    ])
    def test_palindrome_detection(self, text, expected):
        assert is_palindrome(text) is expected

    def test_punctuation_ignored(self):
        assert is_palindrome("A man, a plan, a canal: Panama") is True

    def test_numbers(self):
        assert is_palindrome("12321") is True
        assert is_palindrome("12345") is False


class TestMaskSensitive:
    def test_masks_most_of_string(self):
        assert mask_sensitive("1234567890") == "******7890"

    def test_short_string_fully_masked(self):
        # len("abc") == 3 <= default visible_chars 4
        assert mask_sensitive("abc") == "***"

    def test_exact_boundary_fully_masked(self):
        # len == visible_chars
        assert mask_sensitive("1234") == "****"

    def test_custom_mask_char(self):
        assert mask_sensitive("1234567890", char="#") == "######7890"

    def test_custom_visible_chars(self):
        assert mask_sensitive("1234567890", visible_chars=6) == "****567890"

    def test_empty_string(self):
        assert mask_sensitive("") == ""


class TestCamelToSnake:
    @pytest.mark.parametrize("input_,expected", [
        ("camelCase", "camel_case"),
        ("PascalCase", "pascal_case"),
        ("alreadysnake", "alreadysnake"),
        ("XMLParser", "xml_parser"),
        ("HTTPSConnection", "https_connection"),
        ("getHTTPResponseCode", "get_http_response_code"),
        ("simple", "simple"),
    ])
    def test_conversion(self, input_, expected):
        assert camel_to_snake(input_) == expected

    def test_already_lowercase(self):
        assert camel_to_snake("lowercase") == "lowercase"

    def test_single_uppercase(self):
        assert camel_to_snake("A") == "a"
