# SPDX-License-Identifier: Apache-2.0
"""Input validation for user-supplied person names and e-mail addresses.

Import-safe (no project imports) so both the auth routes and any future caller
share one rule. The charset check is deliberately strict: it accepts Unicode
letters plus a small punctuation set and rejects control characters, angle
brackets, quotes, braces and shell metacharacters — the characters used by
stored-XSS / SSTI / SSRF probe payloads. It also caps length, which SQLite's
``VARCHAR(255)`` does not enforce.
"""

import re

MAX_PERSON_NAME_LENGTH = 100
MAX_EMAIL_LENGTH = 254

# Letters are accepted per-character via ``str.isalpha()`` (any script), so this
# set only needs the allowed non-letter characters.
_ALLOWED_NAME_PUNCT = frozenset(" -.'")

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_person_name(
    value: str | None,
    *,
    required: bool = True,
    field: str = "Имя",
    empty_error: str | None = None,
) -> str | None:
    """Return an error message, or ``None`` when ``value`` is acceptable."""
    name = (value or "").strip()
    if not name:
        if not required:
            return None
        return empty_error or f"{field} не может быть пустым"
    if len(name) > MAX_PERSON_NAME_LENGTH:
        return f"{field} слишком длинное (максимум {MAX_PERSON_NAME_LENGTH} символов)"
    for char in name:
        if char in _ALLOWED_NAME_PUNCT or char.isalpha():
            continue
        return f"{field} содержит недопустимые символы"
    return None


def validate_email(value: str | None) -> str | None:
    """Return an error message, or ``None`` when ``value`` looks like an e-mail."""
    email = (value or "").strip()
    if len(email) < 5:
        return "Почтовый адрес должен быть больше чем 5 символов"
    if len(email) > MAX_EMAIL_LENGTH:
        return f"Почтовый адрес слишком длинный (максимум {MAX_EMAIL_LENGTH} символов)"
    if not _EMAIL_RE.fullmatch(email):
        return "Некорректный почтовый адрес"
    return None


def clean_person_name(value: str | None, *, fallback: str = "") -> str:
    """Best-effort sanitizer for names from external providers (VK/Google).

    We cannot reject an OAuth login over a bad name, so truncate and strip every
    disallowed character, falling back when nothing safe remains.
    """
    name = (value or "").strip()[:MAX_PERSON_NAME_LENGTH]
    cleaned = "".join(char for char in name if char in _ALLOWED_NAME_PUNCT or char.isalpha())
    cleaned = cleaned.strip()
    return cleaned or fallback
