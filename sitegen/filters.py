"""Presentation filters shared by both targets."""

from __future__ import annotations

# Chicago style: articles, coordinating conjunctions and prepositions stay
# lowercase inside a title. Checked against the titles actually in this CV, not
# assembled from a style guide in the abstract.
_LOWER = {
    # articles and coordinating conjunctions
    "a", "an", "and", "as", "but", "for", "nor", "or", "so", "the", "yet",
    # prepositions
    "about", "above", "across", "after", "against", "along", "among", "around",
    "at", "before", "behind", "below", "beneath", "beside", "between", "beyond",
    "by", "despite", "down", "during", "except", "from", "in", "inside", "into",
    "near", "of", "off", "on", "onto", "out", "outside", "over", "past", "per",
    "since", "than", "through", "throughout", "to", "toward", "under", "until",
    "up", "upon", "via", "with", "within", "without",
}

# A title restarts after these, so the next word is capitalized even if it is a
# preposition -- "Armed Conflict? Evidence from ...".
_RESTART = ".:?!—–"


def _cap(word: str) -> str:
    """Capitalize, treating a hyphenated compound as separate words.

    "community-minded" -> "Community-Minded", which is how the CV writes it.
    """
    return "-".join(p[:1].upper() + p[1:] for p in word.split("-"))


def titlecase(text: str) -> str:
    """Title Case a sentence-case string.

    Titles are stored once, in sentence case -- the form the website and the
    BibTeX both use -- and the CV's Title Case is derived. Storing one and
    deriving the other is what stops the two from drifting apart again, as they
    already had on six paper titles.

    Words containing an uppercase letter or a digit are left alone, so "R",
    "200X", "DeclareDesign" and "ICE" survive intact.
    """
    words = text.split(" ")
    out = []
    starts_phrase = True
    for word in words:
        if any(c.isupper() or c.isdigit() for c in word):
            out.append(word)
        elif not starts_phrase and word.lower().strip(_RESTART) in _LOWER:
            out.append(word.lower())
        else:
            out.append(_cap(word))
        starts_phrase = bool(word) and word[-1] in _RESTART
    return " ".join(out)


def authors(names: list[str], conjunction: str = "and") -> str:
    """Render a name list as prose: "A", "A and B", "A, B, and C"."""
    if not names:
        return ""
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return f"{names[0]} {conjunction} {names[1]}"
    return ", ".join(names[:-1]) + f", {conjunction} {names[-1]}"


def downloads(count: int) -> str:
    """Format a CRAN download total the way the site shows it: 85000 -> 85,000.

    Rounded to thousands because the number is refreshed periodically and
    displayed with a leading "~"; false precision would be misleading.
    """
    return f"{round(count / 1000):,},000" if count >= 1000 else str(count)


_MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]


def month_year(value) -> str:
    """Render a YYYY-MM date as "October 2025".

    PyYAML parses an unquoted `2025-10` as the string it is (a full `2025-10-01`
    would become a date object), so both forms are handled.
    """
    if hasattr(value, "year"):
        return f"{_MONTHS[value.month - 1]} {value.year}"
    year, month = str(value).split("-")[:2]
    return f"{_MONTHS[int(month) - 1]} {year}"


def by_date_desc(items: list[dict]) -> list[dict]:
    """Reverse-chronological, stable within a date.

    Ordering is computed so a new entry can be added anywhere in the file and
    still appear in the right place -- the CV's list was previously kept in
    order by hand.
    """
    return sorted(items, key=lambda item: str(item.get("date", "")), reverse=True)


SELF = "Graeme Blair"


def coauthors(names: list[str]) -> list[str]:
    """Everyone except Graeme, in order.

    Not `authors[1:]`: he is not always first. He is second on the Afghanistan
    survey paper and third on the ethics piece, and on the Global South field
    experiments paper the author order is explicitly randomized.
    """
    return [n for n in names if n != SELF]


def rcirc(names: list[str]) -> str:
    """Join names with the randomized-order symbol used by that convention.

    U+24E1 CIRCLED LATIN SMALL LETTER R, not U+24C7 -- the capital. Both look
    like a circled r at a glance and only the lowercase one is in `escape.py`'s
    Unicode table, so the capital passed through to XeLaTeX raw, where Hoefler
    Text has no glyph for it: a missing character in the PDF and a warning
    nobody reads. The site's own convention is the lowercase form too.

    The last name is joined with "and" as well as the symbol, which is how both
    the CV and the site wrote it by hand.
    """
    if len(names) < 2:
        return "".join(names)
    return " \u24e1 ".join(names[:-1]) + f" \u24e1 and {names[-1]}"


def starred(names: list[str], count: int) -> list[str]:
    """Mark the first `count` names with a trailing asterisk.

    Equal-authorship notation: "Rebecca Littman*, Rebecca Wolfe*, Graeme Blair*,
    and Sarah Ryan" means the first three contributed equally. The marker has to
    sit on the names themselves -- a trailing "* Equal authors." with nothing
    starred says only that the footnote exists.
    """
    return [f"{n}*" if i < count else n for i, n in enumerate(names)]


SITE_BASE = "https://graemeblair.com"


def cv_url(pub: dict) -> str | None:
    """The one URL that should wrap this entry's CV line, if any.

    The CV linked most entries to the paper itself. Which link that is comes
    from the same ordered `links` list the site renders, so the two targets
    cannot point at different copies of the same paper -- they already did on
    three entries. Books with no readable copy online (the policing volume)
    have no PDF and no "Read online", so they render unlinked, as before.

    Relative site paths are absolutized: a PDF hyperlink reading `/papers/x.pdf`
    resolves against the reader's filesystem, not the website.
    """
    links = {link["label"]: link.get("url") for link in pub.get("links") or []}
    url = links.get("PDF") or links.get("Read online") or pub.get("url")
    if not url:
        return None
    if url.startswith(("http://", "https://")):
        return url
    return f"{SITE_BASE}/{url.lstrip('/')}"


def by_year_desc(items: list[dict]) -> list[dict]:
    """Newest first, undated entries at the top, YAML order within a year.

    The CV's publication order was maintained by hand and had drifted out of
    order in two places; the YAML order is the *site's*, which is column-major
    (policing, then methods) and so is not a CV ordering at all. Computing it
    means an entry lands in the right place wherever it is added.

    Undated entries sort first because they are forthcoming papers and living
    codebooks -- not yet published, so ahead of everything that has been.
    """
    return sorted(items, key=lambda item: item.get("year") or 10_000, reverse=True)


def cv_link(matter: dict) -> str | None:
    """The one document URL that should wrap this matter's CV line, if any.

    The hand-written CV linked three of fourteen expert-work entries with no
    evident rule. Marking the intended document with `cv_link: true` in the data
    makes the choice explicit and keeps it next to the document it refers to.
    """
    for document in matter.get("documents") or []:
        if document.get("cv_link"):
            return document["url"]
    return None


def targets(item: dict, target: str) -> bool:
    """Does this content item render into the given target ('site' or 'cv')?"""
    return target in item.get("targets", ["site", "cv"])


def for_target(items: list[dict], target: str) -> list[dict]:
    return [item for item in items if targets(item, target)]
