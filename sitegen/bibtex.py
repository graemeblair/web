"""Render BibTeX from content/*.yml.

There used to be a `content/citations.bib` holding a second copy of every
paper: its title, its authors, its journal and year. It was machine-lifted from
the site's own Cite buttons, and by the time it was checked in it disagreed with
the YAML about a dozen things -- two truncated author lists ("and others"), a
chapter typed as an article, a lowercased journal name, six titles in a
different case, and one paper's volume and pages that were another paper's. A
bibliography nobody types is a bibliography nobody proofreads.

So the entries are built here instead, from the same records the site and the CV
render. What used to be the .bib file's own contribution -- volume, issue, pages
-- now sits on the publication, where the CV reads it too.

Output goes to `_site/js/citation.js`, which is what the Cite buttons load.
There is no .bib file anywhere in the tree, and so nothing to keep in step.
"""

from __future__ import annotations

import re

from .content import ContentError

# The order fields are written in. BibTeX does not care, but a stable order
# keeps the Cite modal's copy button handing out the same text every build.
FIELD_ORDER = (
    "title", "author", "editor", "journal", "booktitle", "volume", "number",
    "pages", "year", "publisher", "address", "series", "url", "note",
)

# Characters BibTeX reads as markup rather than as text. `&` is the one that
# actually occurs -- "PS: Political Science & Politics" -- but a stray `%` in a
# title would comment out the rest of the entry just as quietly.
_SPECIAL = {"&": r"\&", "%": r"\%", "#": r"\#", "$": r"\$", "_": r"\_"}


class BibError(ContentError):
    """A citation that cannot be rendered -- reported like any content error."""


def escape(value) -> str:
    return "".join(_SPECIAL.get(char, char) for char in str(value))


def _title(text: str) -> str:
    """A BibTeX title carries no trailing period.

    Titles are stored the way the website prints them, which for an article is a
    sentence ending in a full stop. The citation style supplies its own.
    """
    return text.rstrip(".")


def _pages(text) -> str:
    """"116-133" -> "116--133"; an article number like "eabd3446" passes through.

    The CV writes a page range with one hyphen and BibTeX wants two, so the
    range is stored once, in the form the CV prints, and widened here.
    """
    return re.sub(r"(?<=\d)-(?=\d)", "--", str(text))


def bib_name(name: str, overrides: dict[str, str] | None = None) -> str:
    """"Graeme Blair" -> "Blair, Graeme".

    The last whitespace-separated word is the family name. That holds for every
    name in this bibliography except compound surnames, which no rule can
    recognize -- "Ken Ochieng' Opalo" would come out as "Opalo, Ken Ochieng'".
    Those are listed by hand under `bib_names` in content/publications.yml, so
    the exception sits next to the data instead of buried in this function.
    """
    if overrides and name in overrides:
        return overrides[name]
    parts = name.split()
    if len(parts) < 2:
        return name
    return f"{parts[-1]}, {' '.join(parts[:-1])}"


def name_list(names, overrides: dict[str, str] | None = None) -> str:
    return " and ".join(bib_name(name, overrides) for name in names)


def _numbers(record: dict, fields: dict) -> None:
    """Volume, issue and pages, under the names BibTeX uses for them."""
    if record.get("volume") is not None:
        fields["volume"] = record["volume"]
    if record.get("issue") is not None:
        fields["number"] = record["issue"]
    if record.get("pages") is not None:
        fields["pages"] = _pages(record["pages"])


def publication_entry(pub: dict, overrides: dict[str, str]) -> tuple[str, dict]:
    """(entry type, fields) for one record in content/publications.yml."""
    kind = pub.get("kind", "article")
    names = name_list(pub.get("authors", []), overrides)
    fields: dict = {"title": _title(pub["title"])}

    if kind == "book":
        # An edited volume names editors, not authors -- the same `role: eds`
        # that puts "(eds.)" after the byline in the CV.
        fields["editor" if pub.get("role") == "eds" else "author"] = names
        fields["publisher"] = pub["venue"]
        if pub.get("venue_note"):
            fields["series"] = pub["venue_note"]
        entry_type = "book"
    elif kind == "chapter":
        fields["author"] = names
        fields["booktitle"] = pub["book"]
        fields["editor"] = name_list(pub["editors"], overrides)
        fields["publisher"] = pub["publisher"]
        fields["address"] = pub["publisher_place"]
        _numbers(pub, fields)
        entry_type = "incollection"
    else:
        fields["author"] = names
        if pub.get("venue"):
            fields["journal"] = pub["venue"]
        _numbers(pub, fields)
        entry_type = "article"

    # A paper that is accepted but not yet in an issue has no year on the site
    # or the CV, and BibTeX wants one: `bib_year` is the year it is expected to
    # carry, and it exists only for these.
    year = pub.get("year") or pub.get("bib_year")
    if year is not None:
        fields["year"] = year
    if pub.get("status"):
        fields["note"] = pub["status"]
    return entry_type, fields


def package_entry(pkg: dict, overrides: dict[str, str]) -> tuple[str, dict]:
    """(entry type, fields) for one record in content/software.yml.

    `@manual` is what an R package is: software with a version and a home page,
    not an article. The old .bib called four of the five `@article` with the
    journal set to "The Comprehensive R Archive Network (CRAN)", which is what
    Google Scholar guesses when it meets a package.

    Graeme is not in `authors` there -- the field lists coauthors, the same way
    the site prints "with ..." -- so he is put back at the front here.
    """
    fields = {
        "title": f"{pkg['name']}: {_title(pkg['site_title'])}",
        "author": name_list(["Graeme Blair"] + list(pkg.get("authors", [])), overrides),
        "year": pkg["year"],
        "url": pkg["url"],
    }
    return "manual", fields


def render(key: str, entry_type: str, fields: dict) -> str:
    """One entry, as BibTeX source."""
    unknown = [name for name in fields if name not in FIELD_ORDER]
    if unknown:
        raise BibError(f"{key}: field(s) not in FIELD_ORDER: {', '.join(unknown)}")
    lines = [f"@{entry_type}{{{key},"]
    lines += [
        f"  {name}={{{escape(fields[name])}}},"
        for name in FIELD_ORDER
        if name in fields
    ]
    lines[-1] = lines[-1].rstrip(",")
    return "\n".join(lines + ["}"])


def entries(content: dict) -> dict[str, str]:
    """Every cited record in the content, keyed by its citation key.

    A `cite:` key with no record behind it is what produced the site's one
    broken Cite button -- the ICE paper opened an empty modal and logged an
    error, because the key existed on the page and in no bibliography. There is
    now only one place for it to come from, and a lint that checks every key on
    the page resolves.
    """
    publications = content.get("publications", {})
    overrides = publications.get("bib_names", {})
    out: dict[str, str] = {}

    def add(record: dict, build, where: str) -> None:
        key = record["cite"]
        if key in out:
            raise BibError(f"duplicate citation key {key!r} ({where})")
        try:
            entry_type, fields = build(record, overrides)
        except KeyError as exc:
            # A chapter with no `book`, a package with no `year`. Reported by
            # name rather than as a traceback out of a dict lookup.
            raise BibError(f"{where} ({key}) has no {exc.args[0]}") from exc
        out[key] = render(key, entry_type, fields)

    for pub in publications.get("publications", []):
        if pub.get("cite"):
            add(pub, publication_entry, pub.get("slug", "?"))

    for pkg in content.get("software", {}).get("packages", []):
        if pkg.get("cite"):
            add(pkg, package_entry, pkg.get("name", "?"))

    return out
