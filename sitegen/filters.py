"""Presentation filters shared by both targets."""

from __future__ import annotations

# Words that stay lowercase inside a title unless they lead it. Deliberately
# short: this exists to render six course titles, not to be a general
# title-casing library.
_LOWER = {
    "a", "an", "and", "as", "at", "but", "by", "for", "from", "in", "nor",
    "of", "on", "or", "the", "to", "via", "with",
}


def titlecase(text: str) -> str:
    """Title Case a sentence-case string.

    Course titles are stored in sentence case because that is the CV's house
    style and it is unambiguous; the website's convention is Title Case. Storing
    one and deriving the other is what stops the two from drifting.

    Words containing an uppercase letter or a digit are left alone, so "R",
    "200X" and "DeclareDesign" survive intact.
    """
    words = text.split(" ")
    out = []
    for i, word in enumerate(words):
        if any(c.isupper() or c.isdigit() for c in word):
            out.append(word)
        elif i != 0 and word.lower() in _LOWER:
            out.append(word.lower())
        else:
            out.append(word[:1].upper() + word[1:])
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


def targets(item: dict, target: str) -> bool:
    """Does this content item render into the given target ('site' or 'cv')?"""
    return target in item.get("targets", ["site", "cv"])


def for_target(items: list[dict], target: str) -> list[dict]:
    return [item for item in items if targets(item, target)]
