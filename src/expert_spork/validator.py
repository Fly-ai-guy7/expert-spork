"""Input validation utilities."""

import re
from urllib.parse import urlparse


_EMAIL_RE = re.compile(
    r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
)

_PHONE_RE = re.compile(
    r"^\+?1?\s*[\-.]?\(?\d{3}\)?[\s.\-]?\d{3}[\s.\-]?\d{4}$"
)


def validate_email(email: str) -> bool:
    """Return True if email is a syntactically valid email address."""
    if not isinstance(email, str):
        raise TypeError(f"Expected str, got {type(email).__name__}")
    return bool(_EMAIL_RE.match(email.strip()))


def validate_phone(phone: str) -> bool:
    """Return True if phone matches a common North American phone format."""
    if not isinstance(phone, str):
        raise TypeError(f"Expected str, got {type(phone).__name__}")
    return bool(_PHONE_RE.match(phone.strip()))


def validate_url(url: str, require_https: bool = False) -> bool:
    """Return True if url is a valid HTTP/HTTPS URL.

    Args:
        url: The URL string to validate.
        require_https: If True, only accept https:// URLs.
    """
    if not isinstance(url, str):
        raise TypeError(f"Expected str, got {type(url).__name__}")
    try:
        parsed = urlparse(url.strip())
    except ValueError:
        return False

    if require_https:
        if parsed.scheme != "https":
            return False
    else:
        if parsed.scheme not in ("http", "https"):
            return False

    return bool(parsed.netloc)


def validate_range(value: float, min_val: float, max_val: float) -> bool:
    """Return True if min_val <= value <= max_val."""
    if min_val > max_val:
        raise ValueError(f"min_val ({min_val}) must be <= max_val ({max_val})")
    return min_val <= value <= max_val


def validate_non_empty(value: str) -> bool:
    """Return True if value is a non-empty string after stripping whitespace."""
    if not isinstance(value, str):
        raise TypeError(f"Expected str, got {type(value).__name__}")
    return bool(value.strip())
