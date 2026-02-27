"""Tests for string_utils module.

Coverage gaps:
  - truncate(): suffix customization, max_length == len(text) boundary, TypeError path
  - slugify(): Unicode characters, leading/trailing hyphens, consecutive spaces
  - mask_sensitive(): visible_chars >= len(text) edge case
  - camel_to_snake(): acronyms (e.g. "XMLParser"), numbers in names — not tested at all
  - is_palindrome() — not tested at all
"""

import pytest
from src.string_utils import truncate, slugify, count_words, is_palindrome, mask_sensitive, camel_to_snake


class TestTruncate:
    def test_short_string_unchanged(self):
        assert truncate("hello", 10) == "hello"

    def test_long_string_truncated(self):
        assert truncate("hello world", 8) == "hello..."

    # Missing: truncate with custom suffix
    # Missing: truncate("hi", 2) -> boundary where len == max_length (no truncation)
    # Missing: truncate(123, 5) -> TypeError
    # Missing: truncate("hi", 0) -> ValueError


class TestSlugify:
    def test_basic(self):
        assert slugify("Hello World") == "hello-world"

    def test_special_chars(self):
        assert slugify("Hello, World!") == "hello-world"

    # Missing: slugify("  spaces  ") strips leading/trailing
    # Missing: slugify("") -> ""
    # Missing: slugify("café") (Unicode)


class TestCountWords:
    def test_normal_sentence(self):
        assert count_words("one two three") == 3

    def test_empty_string(self):
        assert count_words("") == 0

    def test_whitespace_only(self):
        assert count_words("   ") == 0

    # Missing: count_words with multiple spaces between words
    # Missing: count_words(None) behavior


class TestMaskSensitive:
    def test_masks_most_of_string(self):
        assert mask_sensitive("1234567890") == "******7890"

    # Missing: string shorter than visible_chars -> all masked
    # Missing: custom char parameter
    # Missing: exact boundary (len == visible_chars)


# is_palindrome is completely untested:
# Missing: is_palindrome("racecar") -> True
# Missing: is_palindrome("A man a plan a canal Panama") -> True (with punctuation/spaces)
# Missing: is_palindrome("hello") -> False
# Missing: is_palindrome("") -> True (empty string)

# camel_to_snake is completely untested:
# Missing: camel_to_snake("camelCase") -> "camel_case"
# Missing: camel_to_snake("HTTPSConnection") -> "https_connection"
# Missing: camel_to_snake("alreadysnake") -> "alreadysnake"
