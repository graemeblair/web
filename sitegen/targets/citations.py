"""Render the Cite buttons' citation data into `_site/js/citation.js`."""

from __future__ import annotations

from pathlib import Path

from markupsafe import Markup

from ..bibtex import entries
from ..envs import html_env


def js_literal(text: str) -> str:
    """Escape BibTeX for the JavaScript template literal it is written into.

    The backslash matters: a field like `Political Science \\& Politics` sits
    inside backticks, and JavaScript reads `\\&` as a plain `&` -- dropping the
    escape before citation-js ever parses the entry.
    """
    return (
        text.replace("\\", "\\\\")
        .replace("`", "\\`")
        .replace("${", "\\${")
    )


def render(content: dict) -> str:
    citations = {
        key: Markup(js_literal(text)) for key, text in entries(content).items()
    }
    return html_env().get_template("citation.js.j2").render(citations=citations)


def write(content: dict, out: Path) -> Path:
    target = out / "js" / "citation.js"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render(content), encoding="utf-8", newline="")
    return target
