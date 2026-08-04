#!/usr/bin/env python3
"""Compare two PDFs by extracted text, page count, and page images.

Gate 4 of the acceptance suite. The CV is the output nobody proofreads line by
line, so it needs the strictest check in the suite:

  text     -- `pdftotext -layout` catches every content and line-break change.
  pages    -- catches a pagination shift caused by an escaping bug.
  images   -- `pdftoppm` catches kerning and spacing regressions that text
              extraction cannot see (e.g. a font falling back).

The footer is normalized out of the text comparison on BOTH sides. It reads
`Last updated \\monthname\\ \\the\\year` (GraemeBlair-CV.tex:546), so the
committed baseline says "Last updated July 2026" and any rebuild today says
something else. That one line is volatile by design and must not be allowed to
fail every run.

Usage:
    python compare_pdf.py BASELINE.pdf BUILT.pdf [--images] [--expect-pages 9]
"""

from __future__ import annotations

import argparse
import difflib
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

VOLATILE = [
    (re.compile(r"Last updated \w+ \d{4}"), "Last updated <DATE>"),
]


def _require(tool: str) -> str:
    path = shutil.which(tool)
    if path is None:
        raise SystemExit(f"{tool} not found -- install poppler (brew install poppler)")
    return path


def text_of(pdf: Path) -> str:
    out = subprocess.run(
        [_require("pdftotext"), "-layout", str(pdf), "-"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    for pattern, replacement in VOLATILE:
        out = pattern.sub(replacement, out)
    return out


def page_count(pdf: Path) -> int:
    out = subprocess.run(
        [_require("pdfinfo"), str(pdf)], check=True, capture_output=True, text=True
    ).stdout
    match = re.search(r"^Pages:\s+(\d+)", out, re.M)
    if not match:
        raise SystemExit(f"could not read page count from {pdf}")
    return int(match.group(1))


def text_diff(baseline: Path, built: Path) -> str:
    """Unified diff of extracted text. Empty string means equal."""
    return "".join(
        difflib.unified_diff(
            text_of(baseline).splitlines(keepends=True),
            text_of(built).splitlines(keepends=True),
            fromfile=str(baseline),
            tofile=str(built),
        )
    )


def image_diffs(baseline: Path, built: Path, dpi: int = 100) -> list[dict]:
    """Render both PDFs to PNGs and compare page by page."""
    from compare_png import compare  # local module, same directory

    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        for pdf, stem in ((baseline, "old"), (built, "new")):
            subprocess.run(
                [_require("pdftoppm"), "-r", str(dpi), "-png", str(pdf), str(tmpdir / stem)],
                check=True,
            )
        olds = sorted(tmpdir.glob("old-*.png"))
        news = sorted(tmpdir.glob("new-*.png"))
        if len(olds) != len(news):
            raise SystemExit(f"page count differs: {len(olds)} vs {len(news)}")
        return [compare(o, n) for o, n in zip(olds, news)]


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("baseline", type=Path)
    p.add_argument("built", type=Path)
    p.add_argument("--images", action="store_true")
    p.add_argument("--expect-pages", type=int, default=None)
    p.add_argument("--threshold", type=float, default=0.001)
    args = p.parse_args(argv)

    failed = False

    pages = page_count(args.built)
    if args.expect_pages is not None and pages != args.expect_pages:
        print(f"FAIL pages: expected {args.expect_pages}, got {pages}")
        failed = True
    else:
        print(f"ok pages: {pages}")

    diff = text_diff(args.baseline, args.built)
    if diff:
        print("FAIL text:")
        sys.stdout.write(diff)
        failed = True
    else:
        print("ok text: identical after footer normalization")

    if args.images:
        for i, r in enumerate(image_diffs(args.baseline, args.built), start=1):
            bad = r["fraction"] > args.threshold or r["size_mismatch"]
            print(f"{'FAIL' if bad else 'ok'} page {i}: {r['fraction']:.5%} bbox={r['bbox']}")
            failed = failed or bad

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
