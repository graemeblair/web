"""Turn plain Unicode content into safe LaTeX.

Content in `content/*.yml` is always plain Unicode: `Tobón`, `&`, `—`, `§`, `ⓡ`.
Never `\\&`, never `{\\'o}`, never `&ldquo;`. Escaping belongs to the renderer,
not the data -- which is precisely why today's sources are inconsistent
(index.html:185 spells quotes `&ldquo;` while :198 uses literal curly quotes, and
GraemeBlair-CV.tex:224 has `Andr{'e}s` with the backslash dropped, a live
typesetting bug in the published PDF).

This runs as the LaTeX environment's `finalize`, so escaping is opt-out
(`| raw_tex`) rather than opt-in. Opt-in escaping is how a bare `&` reaches
XeLaTeX and halts the build -- or worse, how a bare `$` opens math mode and
produces garbled output that compiles successfully.
"""

from __future__ import annotations

# Order matters: backslash first, or every replacement below gets re-escaped.
_SPECIALS = "&%$#_{}"

# Only characters that actually occur in this corpus. An unmapped non-ASCII
# character is reported by `build.py --escape-report` rather than being silently
# passed through to XeTeX.
_UNICODE = {
    "á": r"{\'a}", "é": r"{\'e}", "í": r"{\'i}", "ó": r"{\'o}", "ú": r"{\'u}",
    "Á": r"{\'A}", "É": r"{\'E}", "Í": r"{\'I}", "Ó": r"{\'O}", "Ú": r"{\'U}",
    "à": r"{\`a}", "è": r"{\`e}", "ì": r"{\`i}", "ò": r"{\`o}", "ù": r"{\`u}",
    "ä": r'{\"a}', "ë": r'{\"e}', "ï": r'{\"i}', "ö": r'{\"o}', "ü": r'{\"u}',
    "ñ": r"{\~n}", "Ñ": r"{\~N}", "ç": r"{\c c}",
    "â": r"{\^a}", "ê": r"{\^e}", "î": r"{\^i}", "ô": r"{\^o}", "û": r"{\^u}",
    "ø": r"{\o}", "å": r"{\aa}", "æ": r"{\ae}", "ß": r"{\ss}",
    "ⓡ": r"\textcircled{r}",
    "§": r"\S{}",
    "…": r"\ldots{}",
    " ": "~",
    # The preamble sets Mapping=tex-text (GraemeBlair-CV.tex:24), which turns
    # these ligature forms into real curly quotes and dashes at typeset time.
    # Emitting raw UTF-8 punctuation instead would still typeset, but selects
    # different glyphs in Hoefler Text and changes the pdftotext byte stream.
    "—": "---", "–": "--",
    "“": "``", "”": "''", "‘": "`", "’": "'",
}


class RawTeX(str):
    """A string that is already LaTeX and must not be escaped again."""

    __slots__ = ()


def raw_tex(value) -> RawTeX:
    """Jinja filter: mark a value as pre-built LaTeX (the escaping opt-out)."""
    return RawTeX("" if value is None else str(value))


def latex_escape(value):
    """Jinja `finalize`: escape every interpolated value for LaTeX."""
    if value is None:
        return ""
    if isinstance(value, RawTeX):
        return str(value)
    if not isinstance(value, str):
        return value

    out = value.replace("\\", r"\textbackslash{}")
    for char in _SPECIALS:
        out = out.replace(char, "\\" + char)
    out = out.replace("~", r"\textasciitilde{}").replace("^", r"\textasciicircum{}")
    for char, replacement in _UNICODE.items():
        out = out.replace(char, replacement)
    return out


def unmapped_characters(value: str) -> set[str]:
    """Non-ASCII characters with no LaTeX mapping.

    Feeds `build.py --escape-report`, so a surprise character surfaces as a
    report line instead of as mojibake in a published PDF.
    """
    return {c for c in value if ord(c) > 127 and c not in _UNICODE}
