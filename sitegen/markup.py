"""A closed three-construct inline markup for content strings.

Markdown is not usable here: its `*` and `_` collide with LaTeX, and pulling in
a Markdown dependency to italicize four journal names is not a trade worth
making. So content strings that need emphasis use exactly these three tags and
nothing else:

    [i]...[/i]            <i>...</i>              {\\it ...}
    [b]...[/b]            <b>...</b>              {\\bf ...}
    [link:URL]...[/link]  <a href="URL">...</a>   \\href{URL}{...}

Anything else in a string is literal text. Content is escaped first and only
then wrapped in tag markup, so autoescaping is never blanket-disabled on a
string that came from YAML.
"""

from __future__ import annotations

import re

from markupsafe import Markup, escape as html_escape

from .escape import RawTeX, latex_escape

_TOKEN = re.compile(
    r"\[(?P<close>/)?(?P<tag>i|b|link)(?::(?P<arg>[^\]]*))?\]"
)


class MarkupError(ValueError):
    pass


def _parse(text: str):
    """Yield ('text', s) and ('open'|'close', tag, arg) events."""
    pos = 0
    for m in _TOKEN.finditer(text):
        if m.start() > pos:
            yield ("text", text[pos:m.start()])
        kind = "close" if m.group("close") else "open"
        yield (kind, m.group("tag"), m.group("arg"))
        pos = m.end()
    if pos < len(text):
        yield ("text", text[pos:])


def _render(text: str, wrap, escape):
    out: list[str] = []
    stack: list[tuple[str, str | None, int]] = []
    for event in _parse(text):
        if event[0] == "text":
            out.append(escape(event[1]))
        elif event[0] == "open":
            _, tag, arg = event
            if tag == "link" and not arg:
                raise MarkupError(f"[link:URL] needs a URL in: {text!r}")
            stack.append((tag, arg, len(out)))
        else:
            _, tag, _arg = event
            if not stack or stack[-1][0] != tag:
                raise MarkupError(f"unbalanced [/{tag}] in: {text!r}")
            open_tag, arg, start = stack.pop()
            inner = "".join(out[start:])
            del out[start:]
            out.append(wrap(open_tag, arg, inner))
    if stack:
        raise MarkupError(f"unclosed [{stack[-1][0]}] in: {text!r}")
    return "".join(out)


def to_html(text: str) -> Markup:
    def wrap(tag: str, arg: str | None, inner: str) -> str:
        if tag == "link":
            return f'<a href="{html_escape(arg)}">{inner}</a>'
        return f"<{tag}>{inner}</{tag}>"

    return Markup(_render(text, wrap, lambda s: str(html_escape(s))))


def to_tex(text: str) -> RawTeX:
    def wrap(tag: str, arg: str | None, inner: str) -> str:
        if tag == "link":
            return f"\\href{{{arg}}}{{{inner}}}"
        return f"{{\\{'it' if tag == 'i' else 'bf'} {inner}}}"

    return RawTeX(_render(text, wrap, latex_escape))
