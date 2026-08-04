#!/usr/bin/env python3
"""Extract the structural inventory of an HTML document.

Gate 1 of the acceptance suite. Where normalize_html.py compares *prose*, this
compares the *wiring*: the ids, the links, and the Bootstrap toggle targets that
make the page work. A regression here is a dead link or a button that opens the
wrong thing -- damage a text diff would happily report as "identical".

It also carries two self-checks that do not compare against a baseline at all,
because they are invariants no version of this page should ever violate:

  duplicate_ids        -- today's index.html has one: `listAbstract` appears at
                          both :340 and :544, so the Software tab's `list`
                          chevron opens the Writing tab's abstract.
  unresolved_targets   -- a data-bs-target pointing at zero or >1 elements.

Usage:
    python inventory.py FILE > inventory.json
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

from bs4 import BeautifulSoup


def build(markup: str) -> dict:
    soup = BeautifulSoup(markup, "lxml")

    ids = [el["id"] for el in soup.select("[id]")]
    id_counts = Counter(ids)

    toggles = []
    for el in soup.select("[data-bs-toggle][data-bs-target]"):
        toggles.append([el["data-bs-toggle"], el["data-bs-target"]])

    # A target selector must resolve to exactly one element or the control is
    # ambiguous -- this is what catches the duplicate `listAbstract`.
    unresolved = {}
    for _, target in toggles:
        if target.startswith("#"):
            n = len(soup.select(target))
            if n != 1:
                unresolved[target] = n

    tabs = []
    for el in soup.select("#mainNav a.nav-link"):
        icon = el.find("i")
        tabs.append(
            {
                "id": el.get("id"),
                "href": el.get("href"),
                "label": el.get_text(strip=True),
                "icon": " ".join(icon.get("class", [])) if icon else None,
            }
        )

    return {
        "ids": sorted(ids),
        "duplicate_ids": sorted(k for k, v in id_counts.items() if v > 1),
        "hrefs": sorted({el["href"] for el in soup.select("[href]")}),
        "srcs": sorted({el["src"] for el in soup.select("[src]")}),
        "toggles": sorted(toggles),
        "unresolved_targets": unresolved,
        "citations": sorted({el["data-citation"] for el in soup.select("[data-citation]")}),
        "tabs": tabs,
    }


def build_file(path: str | Path) -> dict:
    return build(Path(path).read_text(encoding="utf-8"))


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        sys.stderr.write(__doc__ or "")
        return 2
    json.dump(build_file(argv[1]), sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
