"""Render the website."""

from __future__ import annotations

from pathlib import Path

from ..envs import html_env


def render(content: dict) -> str:
    return html_env().get_template("index.html.j2").render(**content)


def write(content: dict, out: Path) -> Path:
    target = out / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render(content), encoding="utf-8", newline="")
    return target
