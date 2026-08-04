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
    """Join names with the randomized-order symbol used by that convention."""
    return " \u24c7 ".join(names)


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
