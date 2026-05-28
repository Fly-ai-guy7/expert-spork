"""Input sanitisation for text that flows into LLM prompts.

A rudimentary defence against prompt-injection and resource abuse — not a
guarantee. We strip control characters (which can hide instructions or break
JSON), collapse absurd whitespace runs, and cap length per field. Arabic and
other non-Latin scripts are preserved; only C0/C1 control codes (except
tab/newline) are removed.
"""
from __future__ import annotations

import re
import unicodedata

# Max characters for a single free-text field reaching a prompt.
MAX_FIELD_CHARS = 8000

# Control chars except tab (\t), newline (\n), carriage return (\r).
_CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]")
_WS_RUN_RE = re.compile(r"[ \t]{200,}")
_NL_RUN_RE = re.compile(r"\n{50,}")


def sanitize_text(value: str | None, max_chars: int = MAX_FIELD_CHARS) -> str | None:
    if value is None:
        return None
    # Normalize to NFC so visually-identical strings compare/cap consistently.
    text = unicodedata.normalize("NFC", value)
    text = _CONTROL_RE.sub("", text)
    text = _WS_RUN_RE.sub(" ", text)
    text = _NL_RUN_RE.sub("\n\n", text)
    if len(text) > max_chars:
        text = text[:max_chars]
    return text


def sanitize_citations(citations: list[str] | None, max_items: int = 50) -> list[str]:
    """Citations are short codes like '82/2002:113'. Strip control chars, cap
    length per item, and bound the list size."""
    if not citations:
        return []
    out: list[str] = []
    for c in citations[:max_items]:
        if not isinstance(c, str):
            continue
        cleaned = _CONTROL_RE.sub("", c).strip()
        if cleaned:
            out.append(cleaned[:128])
    return out
