"""Tests for validator — full coverage."""

import pytest
from expert_spork.validator import (
    validate_email,
    validate_phone,
    validate_url,
    validate_range,
    validate_non_empty,
)


# ---------------------------------------------------------------------------
# validate_email
# ---------------------------------------------------------------------------

def test_valid_email():
    assert validate_email("user@example.com") is True


def test_invalid_email_no_at():
    assert validate_email("userexample.com") is False


def test_invalid_email_no_domain():
    assert validate_email("user@") is False


def test_valid_email_subdomain():
    assert validate_email("user@mail.example.co.uk") is True


def test_valid_email_plus_tag():
    assert validate_email("user+tag@example.org") is True


def test_invalid_email_missing_tld():
    assert validate_email("user@example") is False


def test_email_strips_whitespace():
    assert validate_email("  user@example.com  ") is True


def test_email_type_error():
    with pytest.raises(TypeError):
        validate_email(42)


# ---------------------------------------------------------------------------
# validate_phone
# ---------------------------------------------------------------------------

def test_valid_phone_plain():
    assert validate_phone("5551234567") is True


def test_valid_phone_dashes():
    assert validate_phone("555-123-4567") is True


def test_valid_phone_dots():
    assert validate_phone("555.123.4567") is True


def test_valid_phone_with_country_code():
    assert validate_phone("+1 555-123-4567") is True


def test_invalid_phone_too_short():
    assert validate_phone("12345") is False


def test_invalid_phone_letters():
    assert validate_phone("555-CALL-NOW") is False


def test_phone_type_error():
    with pytest.raises(TypeError):
        validate_phone(5551234567)


# ---------------------------------------------------------------------------
# validate_url
# ---------------------------------------------------------------------------

def test_valid_http_url():
    assert validate_url("http://example.com") is True


def test_valid_https_url():
    assert validate_url("https://example.com/path?q=1") is True


def test_invalid_url_no_scheme():
    assert validate_url("example.com") is False


def test_invalid_url_ftp_scheme():
    assert validate_url("ftp://example.com") is False


def test_valid_url_require_https():
    assert validate_url("https://secure.example.com", require_https=True) is True


def test_invalid_url_require_https_rejects_http():
    assert validate_url("http://example.com", require_https=True) is False


def test_invalid_url_no_netloc():
    assert validate_url("https://") is False


def test_url_type_error():
    with pytest.raises(TypeError):
        validate_url(12345)


def test_url_malformed_ipv6_returns_false():
    # urlparse raises ValueError for malformed IPv6 brackets
    assert validate_url("http://[::invalid") is False


# ---------------------------------------------------------------------------
# validate_range
# ---------------------------------------------------------------------------

def test_value_within_range():
    assert validate_range(5.0, 0.0, 10.0) is True


def test_value_at_min_boundary():
    assert validate_range(0.0, 0.0, 10.0) is True


def test_value_at_max_boundary():
    assert validate_range(10.0, 0.0, 10.0) is True


def test_value_below_range():
    assert validate_range(-1.0, 0.0, 10.0) is False


def test_value_above_range():
    assert validate_range(11.0, 0.0, 10.0) is False


def test_range_invalid_bounds():
    with pytest.raises(ValueError, match="min_val"):
        validate_range(5.0, 10.0, 0.0)


# ---------------------------------------------------------------------------
# validate_non_empty
# ---------------------------------------------------------------------------

def test_non_empty_string():
    assert validate_non_empty("hello") is True


def test_empty_string():
    assert validate_non_empty("") is False


def test_whitespace_only_string():
    assert validate_non_empty("   ") is False


def test_non_empty_with_surrounding_whitespace():
    assert validate_non_empty("  hi  ") is True


def test_non_empty_type_error():
    with pytest.raises(TypeError):
        validate_non_empty(None)
