"""Tests for validator — minimal coverage."""

from expert_spork.validator import validate_email


# Only validate_email has any tests.
# validate_phone, validate_url, validate_range, validate_non_empty are untested.


def test_valid_email():
    assert validate_email("user@example.com") is True


def test_invalid_email_no_at():
    assert validate_email("userexample.com") is False


def test_invalid_email_no_domain():
    assert validate_email("user@") is False


# Missing: test_email_with_subdomains
# Missing: test_email_type_error
# Missing: ANY test for validate_phone
# Missing: ANY test for validate_url (including require_https=True branch)
# Missing: ANY test for validate_range
# Missing: ANY test for validate_non_empty
