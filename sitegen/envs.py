"""The two Jinja environments.

HTML and LaTeX cannot share one environment. Jinja's default `{{ }}` and `{% %}`
are unreadable and ambiguous beside `\\href{...}{...}` and `{\\it ...}`, so the
LaTeX environment uses `<<< >>>` / `<<% %>>` delimiters instead.

Parenthesis-style delimiters were tried first and are a trap: CV prose is full
of literal parentheses, so `((( x )))` next to a "(graduate)" annotation gets
parsed as `(((` + the expression `( x )` + `)))`, and the parentheses silently
vanish from the PDF. `<` and `>` appear nowhere in this document.

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

from .escape import raw_tex, tex_url
from .filters import (
    authors, by_date_asc, by_date_desc, by_latest_stage_desc, by_year_desc,
    coauthors, court_runs, cv_link, cv_url, downloads, flatten_stages,
    for_target, month_year, rcirc, starred, titlecase, volume_detail,
)
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
    env.filters["titlecase"] = titlecase
    env.filters["authors"] = authors
    env.filters["downloads"] = downloads
    env.filters["month_year"] = month_year
    env.filters["by_date_desc"] = by_date_desc
    env.filters["by_date_asc"] = by_date_asc
    env.filters["by_latest_stage_desc"] = by_latest_stage_desc
    env.filters["court_runs"] = court_runs
    env.filters["cv_link"] = cv_link
    env.filters["coauthors"] = coauthors
    env.filters["rcirc"] = rcirc
    env.filters["starred"] = starred
    env.filters["for_target"] = lambda items: for_target(items, "site")
    return env


def latex_env() -> Environment:
    from .escape import latex_escape

    env = Environment(
        loader=FileSystemLoader(TEMPLATES / "latex"),
        block_start_string="<<%",
        block_end_string="%>>",
        variable_start_string="<<<",
        variable_end_string=">>>",
        comment_start_string="<<#",
        comment_end_string="#>>",
        autoescape=False,
        finalize=latex_escape,
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
        undefined=StrictUndefined,
    )
    env.filters["raw_tex"] = raw_tex
    env.filters["tex_url"] = tex_url
    env.filters["markup"] = to_tex
    env.filters["titlecase"] = titlecase
    env.filters["authors"] = authors
    env.filters["downloads"] = downloads
    env.filters["month_year"] = month_year
    env.filters["by_date_desc"] = by_date_desc
    env.filters["flatten_stages"] = flatten_stages
    env.filters["cv_link"] = cv_link
    env.filters["coauthors"] = coauthors
    env.filters["rcirc"] = rcirc
    env.filters["starred"] = starred
    env.filters["by_year_desc"] = by_year_desc
    env.filters["cv_url"] = cv_url
    env.filters["volume_detail"] = volume_detail
    env.filters["for_target"] = lambda items: for_target(items, "cv")
    return env
