"""String manipulation utilities."""

import re


def truncate(text, max_length, suffix="..."):
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    if max_length <= 0:
        raise ValueError("max_length must be positive")
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def slugify(text):
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"^-+|-+$", "", text)
    return text


def count_words(text):
    if not text or not text.strip():
        return 0
    return len(text.split())


def is_palindrome(text):
    cleaned = re.sub(r"[^a-zA-Z0-9]", "", text).lower()
    return cleaned == cleaned[::-1]


def mask_sensitive(text, char="*", visible_chars=4):
    if len(text) <= visible_chars:
        return char * len(text)
    return char * (len(text) - visible_chars) + text[-visible_chars:]


def camel_to_snake(name):
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()
