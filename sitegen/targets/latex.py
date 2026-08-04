"""Render the CV source, then lint it before anyone spends 60s on XeLaTeX."""

from __future__ import annotations

import re
from pathlib import Path

from ..envs import latex_env

# Regions where TeX specials are legitimately unescaped, stripped before the
# checks below. Order matters: URLs are removed first, because a `%20` inside one
# would otherwise look like the start of a comment and truncate the line,
# unbalancing its braces.
#
#   \href{URL}{...} and \url{URL} -- hyperref reads the URL argument
#       essentially verbatim, so `_` and `#` in a link are correct as written.
#   #1, #2 ...                    -- macro parameters in \newcommand and friends.
_URL_ARG = re.compile(r"\\(?:href|url)\{[^{}]*\}")
_MACRO_PARAM = re.compile(r"#\d")
_COMMENT = re.compile(r"(?<!\\)%.*$")


class TexLintError(ValueError):
    pass


def render(content: dict) -> str:
    return latex_env().get_template("cv.tex.j2").render(**content)


def lint(source: str) -> list[str]:
    """Cheap checks that turn escaping bugs into legible errors.

    A missing `\\&` halts XeLaTeX with a stack trace 400 lines into the log. A
    missing `\\$` does not halt at all -- it opens math mode and produces
    garbled output that compiles successfully. Catching both here costs
    milliseconds and reports a line number.
    """
    problems: list[str] = []
    depth = 0

    for lineno, raw in enumerate(source.split("\n"), start=1):
        # A URL argument becomes a same-length placeholder so brace counting
        # below still sees its enclosing {}.
        line = _URL_ARG.sub(lambda m: "\\href{URL}", raw)
        line = _COMMENT.sub("", line)
        line = _MACRO_PARAM.sub("", line)

        for char in "&$#_":
            for m in re.finditer(re.escape(char), line):
                before = line[: m.start()]
                # Count trailing backslashes: an odd number means escaped.
                run = len(before) - len(before.rstrip("\\"))
                if run % 2 == 0:
                    problems.append(f"line {lineno}: unescaped {char!r} in {raw.strip()!r}")

        stripped = re.sub(r"\\[{}]", "", line)
        depth += stripped.count("{") - stripped.count("}")

    if depth != 0:
        problems.append(f"unbalanced braces: {depth:+d} across the document")

    if "\\end{document}" not in source:
        problems.append("no \\end{document}")

    # Every \item must start its own line. A draft entry renders as `%\item`,
    # and a LaTeX comment runs to end of line -- so two items sharing a line
    # means one draft can comment out every item after it plus the closing
    # \end{etaremune}. XeLaTeX then fails with "perhaps a missing \item",
    # pointing dozens of lines away from the cause.
    for lineno, raw in enumerate(source.split("\n"), start=1):
        if raw.count("\\item") > 1:
            problems.append(
                f"line {lineno}: {raw.count(chr(92) + 'item')} \\item on one line -- "
                f"a %\\item draft would comment out the rest"
            )

    # An empty list environment is also a "missing \item" error. Commented-out
    # lines are dropped first: this CV keeps several whole list environments
    # commented out as held-back drafts, and they are not errors.
    live = "\n".join(
        ln for ln in source.split("\n") if not ln.lstrip().startswith("%")
    )
    for env in ("etaremune", "itemize", "enumerate"):
        for block in re.findall(
            r"\\begin\{" + env + r"\}(.*?)\\end\{" + env + r"\}", live, re.S
        ):
            if "\\item" not in block:
                problems.append(f"empty {env} environment (no uncommented \\item)")

    return problems


def write(content: dict, out: Path) -> Path:
    source = render(content)
    problems = lint(source)
    if problems:
        raise TexLintError(
            "generated LaTeX failed lint:\n  " + "\n  ".join(problems[:20])
        )
    target = out / "GraemeBlair-CV.tex"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(source, encoding="utf-8", newline="")
    return target
