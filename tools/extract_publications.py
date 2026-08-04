#!/usr/bin/env python3
"""One-off: pull publication records out of the baseline HTML and CV LaTeX.

Prints a reconciliation table, not YAML. The point is that a human decides
every place the two sources disagree -- the extractor never picks a winner.
Safe to delete once content/publications.yml is settled.
"""
from __future__ import annotations

import difflib
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup

BASE = Path("tests/acceptance/baseline")


def site_papers():
    soup = BeautifulSoup((BASE / "index.html").read_text(encoding="utf-8"), "lxml")
    out = []
    for col, heading in enumerate(soup.select("#research h1")):
        column = heading.get_text(strip=True)
        for p in heading.find_parent("div").select("p.paper-title, p.book-title"):
            text = p.get_text(" ", strip=True)
            toggle = p.select_one("[data-bs-target]")
            slug = toggle["data-bs-target"].lstrip("#").replace("Abstract", "") if toggle else None
            panel = soup.select_one(f"#{slug}Abstract") if slug else None
            links, cite, abstract = [], None, None
            if panel:
                for a in panel.select("p.paper-links a"):
                    if a.get("data-citation"):
                        cite = a["data-citation"]
                        links.append(("Cite", None))
                    else:
                        icon = a.find("i")
                        links.append((a.get_text(strip=True),
                                      " ".join(icon.get("class", [])) if icon else None,
                                      a.get("href")))
                el = panel.select_one("p.abstracttext")
                abstract = el.get_text(" ", strip=True) if el else None
            out.append(dict(column=column, slug=slug, text=text, cite=cite,
                            links=links, abstract=abstract,
                            kind="book" if "book-title" in p.get("class", []) else "article"))
    return out


def cv_items():
    tex = (BASE / "GraemeBlair-CV.tex").read_text(encoding="utf-8")
    out = []
    for block in re.findall(r"\\begin{etaremune}(.*?)\\end{etaremune}", tex, re.S):
        for item in re.split(r"\n\s*\\item ", block)[1:]:
            item = item.strip()
            url = re.search(r"\\href{([^}]*)}", item)
            title = re.search(r"``(.+?)''", item, re.S)
            out.append(dict(raw=item, url=url.group(1) if url else None,
                            title=title.group(1).strip() if title else None))
    return out


def norm(s):
    return re.sub(r"[^a-z0-9 ]", "", (s or "").lower()).strip()


def main():
    site, cv = site_papers(), cv_items()
    print(f"site entries: {len(site)}   CV items: {len(cv)}\n")
    used = set()
    for s in site:
        stitle = re.sub(r"^[“\"]|[”\"].*$", "", s["text"]).strip()
        best, score = None, 0.0
        for i, c in enumerate(cv):
            if i in used or not c["title"]:
                continue
            r = difflib.SequenceMatcher(None, norm(stitle), norm(c["title"])).ratio()
            if r > score:
                best, score = i, r
        flag = "SAME " if score > 0.97 else ("DIFFER" if score > 0.55 else "NO MATCH")
        print(f"[{flag}] {score:.2f}  cite={s['cite']}  slug={s['slug']}")
        print(f"   site: {stitle[:110]}")
        if best is not None and score > 0.55:
            used.add(best)
            print(f"   cv:   {cv[best]['title'][:110]}")
        print()
    for i, c in enumerate(cv):
        if i not in used:
            print(f"[CV ONLY] {(c['title'] or c['raw'])[:110]}")


if __name__ == "__main__":
    main()
