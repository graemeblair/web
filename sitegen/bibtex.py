"""Parse content/citations.bib.

This file is the canonical bibliographic record: authors, journal, volume,
number, pages, publisher. Both targets read from it, so nobody types
"115(2): 709-716" into YAML twice and nobody can get it wrong in one place only.

`content/publications.yml` holds presentation instead -- which column a paper
sits in, its abstract, its link row -- and joins to this on the citation key.

Deliberately hand-written rather than a dependency: the file is uniform (it was
machine-generated from the site's own Cite buttons) and this is ~50 lines of
stdlib.
"""

from __future__ import annotations

import re
from pathlib import Path

_ENTRY = re.compile(r"@(\w+)\s*\{\s*([^,]+),(.*?)\n\}", re.S)
_FIELD = re.compile(r"(\w+)\s*=\s*\{(.*?)\}\s*,?\s*(?=\n\s*\w+\s*=|\s*$)", re.S)


def _flip(name: str) -> str:
    """"Blair, Graeme" -> "Graeme Blair"; names already in given-first order pass through."""
    name = name.strip()
    if "," not in name:
        return name
    family, given = name.split(",", 1)
    return f"{given.strip()} {family.strip()}".strip()


def parse_authors(field: str) -> list[str]:
    return [_flip(part) for part in re.split(r"\s+and\s+", field) if part.strip()]


def parse(text: str) -> dict[str, dict]:
    entries: dict[str, dict] = {}
    for kind, key, body in _ENTRY.findall(text):
        fields = {
            name.lower(): re.sub(r"\s+", " ", value).strip()
            for name, value in _FIELD.findall(body)
        }
        fields["type"] = kind.lower()
        fields["key"] = key.strip()
        if "author" in fields:
            fields["authors"] = parse_authors(fields["author"])
        entries[key.strip()] = fields
    return entries


def load(path: Path) -> dict[str, dict]:
    return parse(path.read_text(encoding="utf-8"))
