#!/usr/bin/env python3
"""Canonicalize an HTML document so two versions can be compared for meaning.

Gate 2 of the acceptance suite. The generator is licensed to normalize
indentation, entity form, and attribute order -- today's index.html mixes tab
indentation (lines 591-676) with two-space indentation everywhere else -- but it
is NOT licensed to change a word of text, a URL, or the document structure.

This module throws away exactly what the generator may change and keeps
everything else, producing a line-oriented form that `diff -u` can report on
usefully.

Discarded:
  - comments
  - `class` and `style` (purely presentational, and the generator reformats them)
  - internal identifier attributes -- `id` and the attributes that reference one.
    These name things; they are not content. Renaming a collapse target changes
    no rendered pixel, and a generator deriving ids from a slug will rename some.
    Wiring is checked precisely, and with an expected-diff escape hatch, by
    inventory.py -- so checking it a second time here only produces failures
    with no way to register a deliberate change.
  - all inter-element whitespace; runs inside text collapse to one space
  - HTML entity spelling (`&oacute;` and a literal `o-acute` compare equal)

Kept:
  - element nesting and order
  - `href` and `src` -- destinations are content, not names
  - every other attribute, sorted by name
  - every non-empty text run

Usage:
    python normalize_html.py FILE            # write canonical form to stdout
    python normalize_html.py A B             # unified diff of A against B
"""

from __future__ import annotations

import difflib
import html
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup, Comment, NavigableString, Doctype

# Presentational only, and reformatted freely by the generator.
DROP_ATTRS = {"class", "style"}

# Internal names and references to them. See the module docstring: inventory.py
# owns this, because only it can distinguish a registered rename from a
# regression.
DROP_ATTRS |= {
    "id",
    "aria-controls",
    "aria-labelledby",
    "data-bs-target",
    "for",
}

_WS = re.compile(r"\s+")


def _collapse(text: str) -> str:
    return _WS.sub(" ", html.unescape(text)).strip()


def _render_open_tag(el) -> str:
    attrs = []
    for name, value in sorted(el.attrs.items()):
        if name in DROP_ATTRS:
            continue
        if isinstance(value, list):  # e.g. rel="preconnect stylesheet"
            value = " ".join(value)
        attrs.append(f"{name}={_collapse(str(value))!r}")
    joined = (" " + " ".join(attrs)) if attrs else ""
    return f"<{el.name}{joined}>"


def canonicalize(markup: str) -> str:
    """Return the canonical line-per-node form of an HTML document."""
    soup = BeautifulSoup(markup, "lxml")
    lines: list[str] = []

    def walk(node, depth: int) -> None:
        for child in node.children:
            if isinstance(child, (Comment, Doctype)):
                continue
            if isinstance(child, NavigableString):
                text = _collapse(str(child))
                if text:
                    lines.append(f"{'  ' * depth}#text {text}")
                continue
            lines.append(f"{'  ' * depth}{_render_open_tag(child)}")
            walk(child, depth + 1)

    walk(soup, 0)
    return "\n".join(lines) + "\n"


def canonicalize_file(path: str | Path) -> str:
    return canonicalize(Path(path).read_text(encoding="utf-8"))


def diff(a: str | Path, b: str | Path) -> str:
    """Unified diff of two files' canonical forms. Empty string means equal."""
    return "".join(
        difflib.unified_diff(
            canonicalize_file(a).splitlines(keepends=True),
            canonicalize_file(b).splitlines(keepends=True),
            fromfile=str(a),
            tofile=str(b),
        )
    )


def main(argv: list[str]) -> int:
    if len(argv) == 2:
        sys.stdout.write(canonicalize_file(argv[1]))
        return 0
    if len(argv) == 3:
        out = diff(argv[1], argv[2])
        sys.stdout.write(out)
        return 1 if out else 0
    sys.stderr.write(__doc__ or "")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
