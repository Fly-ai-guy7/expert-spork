"""String manipulation utilities."""

import re
import unicodedata


def slugify(text: str) -> str:
    """Convert text to a URL-safe slug.

    Example: "Hello World!" -> "hello-world"
    """
    if not isinstance(text, str):
        raise TypeError(f"Expected str, got {type(text).__name__}")
    # Normalize unicode characters
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower().strip()
    # Replace non-alphanumeric characters with hyphens
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    text = re.sub(r"^-+|-+$", "", text)
    return text


def truncate(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to max_length, appending suffix if truncated.

    Example: truncate("Hello World", 8) -> "Hello..."
    """
    if not isinstance(text, str):
        raise TypeError(f"Expected str, got {type(text).__name__}")
    if max_length < len(suffix):
        raise ValueError(f"max_length must be >= len(suffix) ({len(suffix)})")
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def word_count(text: str) -> dict[str, int]:
    """Return a frequency map of words in text (case-insensitive).

    Example: word_count("the cat and the dog") -> {"the": 2, "cat": 1, ...}
    """
    if not isinstance(text, str):
        raise TypeError(f"Expected str, got {type(text).__name__}")
    counts: dict[str, int] = {}
    for word in re.findall(r"\b\w+\b", text.lower()):
        counts[word] = counts.get(word, 0) + 1
    return counts


def camel_to_snake(name: str) -> str:
    """Convert camelCase or PascalCase to snake_case.

    Example: "MyClassName" -> "my_class_name"
    """
    name = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    return name.lower()


def snake_to_camel(name: str) -> str:
    """Convert snake_case to camelCase.

    Example: "my_variable_name" -> "myVariableName"
    """
    parts = name.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])


def is_palindrome(text: str) -> bool:
    """Return True if text is a palindrome (ignoring case and non-alphanumeric chars).

    Example: is_palindrome("A man a plan a canal Panama") -> True
    """
    cleaned = re.sub(r"[^a-z0-9]", "", text.lower())
    return cleaned == cleaned[::-1]
