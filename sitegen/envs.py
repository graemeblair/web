"""The two Jinja environments.

HTML and LaTeX cannot share one environment. Jinja's default `{{ }}` and `{% %}`
are unreadable and ambiguous beside `\\href{...}{...}` and `{\\it ...}`, so the
LaTeX environment uses `((( )))` / `((* *))` delimiters instead.

Two settings carry most of the safety:

  finalize=latex_escape   Escaping is opt-out (`| raw_tex`), not opt-in. A bare
                          `&` that slips through halts XeLaTeX; a bare `$` opens
                          math mode and produces garbled output that compiles
                          *successfully*, which is far worse.

  undefined=StrictUndefined
                          A renamed or misspelled YAML key fails the build
                          instead of rendering as empty. The CV is a PDF nobody
                          proofreads line by line -- a silently missing field
                          could ship for months.
"""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined
from markupsafe import Markup

from .escape import raw_tex
from .markup import to_html, to_tex

REPO = Path(__file__).resolve().parent.parent
TEMPLATES = REPO / "templates"
STATIC = REPO / "static"


def _inline(relative: str) -> Markup:
    """Return a file from static/ for inlining into a <style> or <script>.

    The source stays a real, lintable .css/.js file while the rendered page
    keeps its zero-latency inline block.
    """
    return Markup((STATIC / relative).read_text(encoding="utf-8").rstrip("\n"))


def html_env() -> Environment:
    env = Environment(
        loader=FileSystemLoader(TEMPLATES / "html"),
        autoescape=True,
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
        undefined=StrictUndefined,
    )
    env.globals["inline"] = _inline
    env.filters["markup"] = to_html
    return env


def latex_env() -> Environment:
    from .escape import latex_escape

    env = Environment(
        loader=FileSystemLoader(TEMPLATES / "latex"),
        block_start_string="((*",
        block_end_string="*))",
        variable_start_string="(((",
        variable_end_string=")))",
        comment_start_string="((=",
        comment_end_string="=))",
        autoescape=False,
        finalize=latex_escape,
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
        undefined=StrictUndefined,
    )
    env.filters["raw_tex"] = raw_tex
    env.filters["markup"] = to_tex
    return env
