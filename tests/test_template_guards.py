# -*- coding: utf-8 -*-
"""Structural guards: CSP-safe templates, credential autocomplete, no silent
exception swallowing.

These scan sources so a regression fails loudly in CI even without a browser.

Inline event handlers are dead under the site's strict nonce CSP
(script-src has no 'unsafe-inline'), so any new ``onX="..."`` attribute or
``javascript:`` href is a bug — the 2026-08-31 dead "Забыли пароль?" button
was exactly that. Wire behavior through a nonce <script> listener instead.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES_DIR = ROOT / "src" / "templates"
SRC_DIR = ROOT / "src"

_EVENT_ATTR = re.compile(r"\son[a-z]+\s*=", re.IGNORECASE)


def _strip_comments_and_scripts(text: str) -> str:
    """Remove HTML comments and <script> blocks before scanning attributes.

    Nonce scripts legitimately register listeners, so their contents must not
    be flagged; comments may reference long-dead inline handlers.
    """
    return re.sub(
        r"<script\b.*?</script>",
        " ",
        re.sub(r"<!--.*?-->", " ", text, flags=re.S),
        flags=re.S | re.I,
    )


def _line_number(text: str, start: int) -> int:
    return text[:start].count("\n") + 1


class TestTemplateGuards:
    def test_no_inline_event_handlers(self):
        offenders = []
        for p in sorted(TEMPLATES_DIR.rglob("*.html")):
            text = _strip_comments_and_scripts(p.read_text(encoding="utf-8"))
            offenders.extend(
                f"{p.relative_to(ROOT)}:{_line_number(text, m.start())}"
                for m in _EVENT_ATTR.finditer(text)
            )
        assert not offenders, (
            "Inline event handlers are blocked by the strict nonce CSP; wire "
            f"them via a nonce <script> listener instead. Found: {offenders}"
        )

    def test_no_javascript_hrefs(self):
        offenders = []
        for p in sorted(TEMPLATES_DIR.rglob("*.html")):
            text = _strip_comments_and_scripts(p.read_text(encoding="utf-8"))
            offenders.extend(
                f"{p.relative_to(ROOT)}:{_line_number(text, m.start())}"
                for m in re.finditer(r"href\s*=\s*['\"]\s*javascript:", text, re.IGNORECASE)
            )
        assert not offenders, f"javascript: hrefs found in {offenders}"

    def test_logout_only_in_dropdown(self):
        """Logout must be a dropdown item, never an always-visible nav link.

        The 2026-08-31 "Exit under Profile always" regression rendered logout
        as a bare ``nav-link``; it belongs in the profile dropdown so it is not
        visible until the user opens the menu.
        """
        offenders = []
        for p in sorted(TEMPLATES_DIR.rglob("*.html")):
            text = _strip_comments_and_scripts(p.read_text(encoding="utf-8"))
            for m in re.finditer(r"url_for\(['\"]logout['\"]\)", text):
                tag_start = text.rfind("<a", 0, m.start())
                tag_end = text.find(">", m.start())
                if tag_start < 0 or tag_end < 0:
                    offenders.append(f"{p.relative_to(ROOT)}:{_line_number(text, m.start())}")
                    continue
                tag = text[tag_start:tag_end]
                if "list-group-item" not in tag:
                    offenders.append(f"{p.relative_to(ROOT)}:{_line_number(text, m.start())}")
        assert not offenders, (
            "Logout must be reachable only from the profile dropdown; an "
            f"always-visible Exit link regressed. Found: {offenders}"
        )

    def test_autocomplete_on_credential_inputs(self):
        """Password/e-mail/login inputs must declare autocomplete.

        Read-only or disabled fields are exempt (profile e-mail, etc.).
        """
        offenders = []
        for p in sorted(TEMPLATES_DIR.rglob("*.html")):
            text = p.read_text(encoding="utf-8")
            for m in re.finditer(r"<input\b[^>]*>", text):
                tag = m.group(0)
                if not ('type="password"' in tag or 'type="email"' in tag or 'type="login"' in tag):
                    continue
                if "readonly" in tag or "disabled" in tag:
                    continue
                if "autocomplete" not in tag:
                    offenders.append(f"{p.relative_to(ROOT)}:{_line_number(text, m.start())}")
        assert not offenders, (
            "Credential inputs must declare autocomplete (password managers, "
            f"no-JS UX). Missing in: {offenders}"
        )

    def test_no_silent_exception_swallow(self):
        """except-clauses whose body is only ``pass`` must be acknowledged.

        Silent swallowing hides real failures; annotate intentional best-effort
        swallows with ``# noqa`` on the except line.
        """
        offenders = []
        for p in sorted(SRC_DIR.rglob("*.py")):
            lines = p.read_text(encoding="utf-8").splitlines()
            for i, line in enumerate(lines):
                if not re.match(r"\s*except\b", line):
                    continue
                if "# noqa" in line:
                    continue
                body = [b.strip() for b in lines[i + 1 : i + 2]]
                if body and body[0] == "pass":
                    offenders.append(f"{p.relative_to(ROOT)}:{i + 1}")
        assert not offenders, (
            "Silent `except: pass` blocks hide failures. Log the error or "
            f"annotate with `# noqa: silent-except`. Found in: {offenders}"
        )
