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

sys.path.insert(0, str(Path(__file__).parent))

VOLATILE = [
    (re.compile(r"Last updated \w+ \d{4}"), "Last updated <DATE>"),
]

# Hoefler Text sets "fi" and "fl" as single glyphs and `pdftotext` extracts them
# as the Unicode ligature characters, so "conflict" comes back as "conﬂict" and
# no reason registered against the source ever matches it. Undone on both sides:
# the ligature is a property of the typeface, not of the text.
LIGATURES = str.maketrans({
    "ﬁ": "fi", "ﬂ": "fl", "ﬀ": "ff", "ﬃ": "ffi", "ﬄ": "ffl", "ﬅ": "ft", "ﬆ": "st",
})


def _require(tool: str) -> str:
    path = shutil.which(tool)
    if path is None:
        raise SystemExit(f"{tool} not found -- install poppler (brew install poppler)")
    return path


def _normalize(text: str) -> str:
    """Strip indentation `pdftotext -layout` computes from column positions.

    `-layout` pads each line to preserve horizontal position, so a centred page
    number moves left or right when anything else on the page changes width.
    That is not a content change, and left unhandled it reports every page whose
    text reflowed at all. Words are still compared exactly.
    """
    lines = []
    for line in text.translate(LIGATURES).splitlines():
        line = line.strip()
        # Drop the folio. A bare page number is furniture, and when content
        # crosses a page break it shifts to a different line of the extracted
        # text and reads as a change. No CV content is a bare number on its own
        # line, so nothing real is lost.
        if line.isdigit():
            continue
        for pattern, replacement in VOLATILE:
            line = pattern.sub(replacement, line)
        lines.append(line + "\n")
    return _unwrap_entries(lines)


_ITEM = re.compile(r"^(\d+)\.\s+(?=\S)")


def _unwrap_entries(lines: list[str]) -> str:
    """Reflow each numbered publication entry back onto one line.

    `pdftotext` breaks an entry wherever the typeset column ended, so a title
    the CV changed arrives split across two lines with a soft hyphen in the
    middle -- "...Reduce Crime? Evidence from Six Coordinated Field Ex-" /
    "periments...". A registered reason names the fragment that changed, and no
    fragment longer than about ten words survives that. Registering the wrapped
    halves instead would tie every reason to the current pagination: reword an
    entry three items above and the keys below it stop matching.

    So the wrapping is undone before comparing, which is also what makes a
    change legible in the failure output. The entry number is dropped with it:
    it comes from the entry's position, the list is reverse-numbered, and
    inserting one paper renumbers every paper below it. Order is checked
    directly by test_gate4_cv_publications_are_in_order.
    """
    out: list[str] = []
    in_entry = False
    for line in lines:
        stripped = line.rstrip("\n")
        if _ITEM.match(stripped):
            out.append(_ITEM.sub("", stripped))
            in_entry = True
        elif in_entry and stripped.strip():
            previous = out[-1]
            # A trailing hyphen is `pdftotext`'s rendering of TeX's
            # hyphenation, not a character in the text.
            if previous.endswith("-"):
                out[-1] = previous[:-1] + stripped.strip()
            else:
                out[-1] = previous + " " + stripped.strip()
        else:
            out.append(stripped)
            in_entry = False
    return "".join(line + "\n" for line in out)


def text_of(pdf: Path) -> str:
    out = subprocess.run(
        [_require("pdftotext"), "-layout", str(pdf), "-"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    return _normalize(out)


def page_texts(pdf: Path) -> list[str]:
    """Extracted text, one entry per page, with the volatile footer normalized."""
    out = []
    for page in range(1, page_count(pdf) + 1):
        text = subprocess.run(
            [_require("pdftotext"), "-layout", "-f", str(page), "-l", str(page),
             str(pdf), "-"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        out.append(_normalize(text))
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
    """Compare page images, but only for pages whose text is unchanged.

    The image comparison exists to catch what text extraction cannot see:
    kerning shifts, spacing regressions, a font quietly falling back. It cannot
    say anything useful about a page whose text has legitimately changed --
    different words are different pixels, and reflow moves everything below
    them. Comparing those pages produces failures that only ever mean "yes, the
    thing you changed did change".

    So pages are matched to their own text first. Pages that changed textually
    are reported and skipped; the rest must be pixel-identical, which keeps the
    check sharp everywhere it can still say something.
    """
    from compare_png import compare  # local module, same directory

    old_text = page_texts(baseline)
    new_text = page_texts(built)

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

        results = []
        for i, (o, n) in enumerate(zip(olds, news)):
            if i < len(old_text) and i < len(new_text) and old_text[i] != new_text[i]:
                results.append({"page": i + 1, "skipped": "text changed on this page"})
                continue
            result = compare(o, n)
            result["page"] = i + 1
            results.append(result)
        return results


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
        # Content that has deliberately changed since the baseline was frozen
        # is registered in expected_diffs.py with a reason. Anything else fails.
        from expected_diffs import unexplained_diff_lines

        unexplained = unexplained_diff_lines(diff)
        if unexplained:
            print("FAIL text -- changes with no registered reason:")
            print("\n".join(unexplained))
            failed = True
        else:
            print(f"ok text: {len(diff.splitlines())} diff lines, all registered")
    else:
        print("ok text: identical after footer normalization")

    if args.images:
        for r in image_diffs(args.baseline, args.built):
            if r.get("skipped"):
                print(f"skip page {r['page']}: {r['skipped']}")
                continue
            bad = r["fraction"] > args.threshold or r["size_mismatch"]
            verdict = "FAIL" if bad else "ok"
            print(f"{verdict} page {r['page']}: {r['fraction']:.5%} bbox={r['bbox']}")
            failed = failed or bad

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
