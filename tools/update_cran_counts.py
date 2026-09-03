#!/usr/bin/env python3
"""Refresh CRAN download totals into content/cran_downloads.yml.

    python3 tools/update_cran_counts.py [--dry-run]

Then run `python build.py` and commit both files.

This used to rewrite index.html directly with a regex, and dropped a
`.backup.<timestamp>` copy of the page into the repo root each time. Both
behaviours are gone: it now writes one small generated YAML file, and git is
the backup. The regex approach would also have silently desynced the page from
content/software.yml.

The fetch logic is unchanged -- cranlogs first, METACRAN as a fallback.
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

import requests

REPO = Path(__file__).resolve().parent.parent
TARGET = REPO / "content" / "cran_downloads.yml"

PACKAGES = ["DeclareDesign", "estimatr", "fabricatr", "list", "rr"]

HEADER = """\
# MACHINE-WRITTEN. Do not hand-edit -- run tools/update_cran_counts.py.
#
# Total CRAN downloads per package, as integers. The site formats them
# (85000 -> "~85,000 downloads"); the CV never shows them.
#
# Kept in its own file so the refresh script rewrites a small generated file
# instead of reaching into software.yml and destroying its comments.
#
# checked: {checked}
"""


def get_cran_downloads(package: str) -> int | None:
    """Total downloads for a package. Tries cranlogs, then METACRAN."""
    try:
        response = requests.get(
            f"https://cranlogs.r-pkg.org/downloads/total/{package}", timeout=10
        )
        response.raise_for_status()
        data = response.json()
        if data.get("downloads", 0) > 0:
            print(f"  {package}: {data['downloads']:,} (cranlogs)")
            return data["downloads"]
    except requests.RequestException as exc:
        print(f"  cranlogs failed for {package}: {exc}", file=sys.stderr)

    try:
        response = requests.get(
            f"https://api.r-hub.io/packages/{package}/downloads", timeout=10
        )
        response.raise_for_status()
        data = response.json()
        if data.get("count", 0) > 0:
            print(f"  {package}: {data['count']:,} (METACRAN)")
            return data["count"]
    except requests.RequestException as exc:
        print(f"  METACRAN failed for {package}: {exc}", file=sys.stderr)

    print(f"  {package}: no data", file=sys.stderr)
    return None


def render(counts: dict[str, int], checked: str) -> str:
    lines = [HEADER.format(checked=checked), ""]
    lines += [f"{name}: {counts[name]}" for name in PACKAGES if name in counts]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="print, do not write")
    args = parser.parse_args(argv)

    print("Fetching CRAN download totals...")
    counts = {}
    for package in PACKAGES:
        count = get_cran_downloads(package)
        if count is not None:
            counts[package] = count

    # Every package must resolve. A partial write would drop a package from the
    # file, and build.py would then fail on the missing key -- a confusing way
    # to learn that one API call timed out.
    missing = [p for p in PACKAGES if p not in counts]
    if missing:
        print(f"\nrefusing to write: no data for {', '.join(missing)}", file=sys.stderr)
        return 1

    output = render(counts, date.today().isoformat())

    if args.dry_run:
        sys.stdout.write("\n" + output)
        return 0

    TARGET.write_text(output, encoding="utf-8")
    print(f"\nwrote {TARGET.relative_to(REPO)}")
    print("next: python build.py && git add content/cran_downloads.yml")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
