"""The acceptance gates.

Gate 1  structural inventory equality      (ids, links, toggles, citations, tabs)
Gate 2  normalized text equality           (prose, after whitespace/entity normalization)
Gate 4  CV text, page count, page images
Gate 5  content lints                      (permanent invariants, not baseline comparisons)

Gate 3 (browser screenshots and live behavior) needs a browser and runs
separately -- see tests/acceptance/README.md.

Until `build.py` produces output, the gates that need `_site/` skip. The
self-check tests below always run: they prove the harness itself is trustworthy
by comparing the baseline to itself, so that once the generator exists a red
gate means a real regression rather than a broken comparator.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

import inventory
import normalize_html
from expected_diffs import describe, is_expected

HERE = Path(__file__).parent
BASELINE = HERE / "baseline"
REPO = HERE.parent.parent
SITE = REPO / "_site"

BASE_HTML = BASELINE / "index.html"
BASE_PDF = BASELINE / "GraemeBlair-CV.pdf"
BUILT_HTML = SITE / "index.html"
BUILT_PDF = SITE / "GraemeBlair-CV.pdf"

# Frozen at the baseline commit. A change here is a pagination or layout event
# that must be explained, not absorbed.
BASELINE_PAGES = 9

needs_build = pytest.mark.skipif(
    not BUILT_HTML.exists(), reason="no _site/index.html yet -- run build.py"
)
needs_pdf = pytest.mark.skipif(
    not BUILT_PDF.exists(), reason="no _site/GraemeBlair-CV.pdf yet"
)


# --------------------------------------------------------------------------
# Harness self-checks. These prove the comparators work before we trust them.
# --------------------------------------------------------------------------


def test_canonicalizer_is_stable():
    once = normalize_html.canonicalize_file(BASE_HTML)
    twice = normalize_html.canonicalize(once)
    assert once, "canonicalizer produced nothing"
    # Canonicalizing the canonical form must not lose lines to a second pass of
    # whitespace collapsing.
    assert len(once.splitlines()) >= len(twice.splitlines())


def test_baseline_matches_itself():
    assert normalize_html.diff(BASE_HTML, BASE_HTML) == ""
    assert inventory.build_file(BASE_HTML) == inventory.build_file(BASE_HTML)


def test_canonicalizer_detects_a_word_change():
    """A one-word edit must surface. Guards against a comparator that always passes."""
    markup = BASE_HTML.read_text(encoding="utf-8")
    mutated = markup.replace("Professor of Political Science", "Professor of Basketry", 1)
    assert mutated != markup
    assert normalize_html.canonicalize(markup) != normalize_html.canonicalize(mutated)


def test_canonicalizer_ignores_whitespace_and_entities():
    """The normalizations the generator IS licensed to make must compare equal."""
    a = "<p>Santiago &oacute; &ldquo;x&rdquo;</p>"
    b = "<p>\n   Santiago ó\n   “x”\n</p>"
    assert normalize_html.canonicalize(a) == normalize_html.canonicalize(b)


def test_canonicalizer_ignores_class_and_style_but_not_href():
    a = '<a class="x" style="color:red" href="/a">t</a>'
    b = '<a href="/a">t</a>'
    c = '<a href="/b">t</a>'
    assert normalize_html.canonicalize(a) == normalize_html.canonicalize(b)
    assert normalize_html.canonicalize(a) != normalize_html.canonicalize(c)


# --------------------------------------------------------------------------
# Baseline bug pins. These record defects that exist TODAY, so that fixing one
# is a visible, deliberate event rather than an accident.
# --------------------------------------------------------------------------

KNOWN_BASELINE_DUPLICATE_IDS = ["listAbstract"]
KNOWN_BASELINE_UNDEFINED_CITATIONS = ["blair2025ice"]


def test_baseline_known_duplicate_ids():
    """index.html:340 and :544 both use `listAbstract`.

    Consequence: the Software tab's `list` chevron opens the Writing tab's
    "Statistical analysis of list experiments" abstract. Fixing it is a visible
    behavior change and needs an expected_diffs entry.
    """
    inv = inventory.build_file(BASE_HTML)
    assert inv["duplicate_ids"] == KNOWN_BASELINE_DUPLICATE_IDS


def test_baseline_has_an_undefined_citation_key():
    """index.html:189 cites blair2025ice, which citation.js never defines.

    Consequence: the ICE paper's Cite button is a console error and an empty
    modal.
    """
    used = set(inventory.build_file(BASE_HTML)["citations"])
    defined = set(_citation_keys(BASELINE / "citation.js"))
    assert sorted(used - defined) == KNOWN_BASELINE_UNDEFINED_CITATIONS


def _citation_keys(js: Path) -> list[str]:
    import re

    text = js.read_text(encoding="utf-8")
    return re.findall(r"^\s*'([A-Za-z0-9_]+)':\s*`", text, re.M)


# --------------------------------------------------------------------------
# Gate 1 -- structural inventory
# --------------------------------------------------------------------------


@needs_build
def test_gate1_inventory_matches_baseline():
    base = inventory.build_file(BASE_HTML)
    built = inventory.build_file(BUILT_HTML)

    problems: list[str] = []
    for field, kind in (("ids", "id"), ("hrefs", "href"), ("srcs", "src"),
                        ("citations", "citation")):
        missing = set(base[field]) - set(built[field])
        added = set(built[field]) - set(base[field])
        for key in sorted(missing | added):
            if not is_expected(kind, key):
                verb = "removed" if key in missing else "added"
                problems.append(f"{verb} {describe(kind, key)}")

    if base["toggles"] != built["toggles"]:
        problems.append("data-bs-toggle/target pairs differ")
    if base["tabs"] != built["tabs"]:
        problems.append("nav tab set or order differs")

    assert not problems, "\n".join(problems)


@needs_build
def test_gate1_every_toggle_target_resolves_once():
    """No duplicate or dangling data-bs-target in the BUILT site.

    The baseline violates this (`listAbstract`); the generated site must not.
    """
    inv = inventory.build_file(BUILT_HTML)
    assert inv["unresolved_targets"] == {}


# --------------------------------------------------------------------------
# Gate 2 -- normalized text
# --------------------------------------------------------------------------


@needs_build
def test_gate2_normalized_text_matches_baseline():
    diff = normalize_html.diff(BASE_HTML, BUILT_HTML)
    assert diff == "", diff


@needs_build
@pytest.mark.skipif(shutil.which("tidy") is None, reason="tidy not installed")
def test_gate2_built_html_is_valid():
    """`tidy` must report zero errors on the built page.

    Today's hand-written index.html fails this on the duplicate id, which is
    exactly the point of the check.
    """
    result = subprocess.run(
        ["tidy", "-errors", "-quiet", "-utf8", str(BUILT_HTML)],
        capture_output=True,
        text=True,
    )
    errors = [ln for ln in result.stderr.splitlines() if " Error: " in ln]
    assert not errors, "\n".join(errors)


# --------------------------------------------------------------------------
# Gate 4 -- the CV
# --------------------------------------------------------------------------


@needs_pdf
def test_gate4_cv_page_count():
    import compare_pdf

    assert compare_pdf.page_count(BUILT_PDF) == BASELINE_PAGES


@needs_pdf
def test_gate4_cv_text_matches_baseline():
    import compare_pdf

    diff = compare_pdf.text_diff(BASE_PDF, BUILT_PDF)
    assert diff == "", diff


@needs_pdf
@pytest.mark.skipif(shutil.which("pdftoppm") is None, reason="poppler not installed")
def test_gate4_cv_page_images_match_baseline():
    import compare_pdf

    bad = [
        f"page {i}: {r['fraction']:.5%} bbox={r['bbox']}"
        for i, r in enumerate(compare_pdf.image_diffs(BASE_PDF, BUILT_PDF), start=1)
        if r["fraction"] > 0.001 or r["size_mismatch"]
    ]
    assert not bad, "\n".join(bad)


# --------------------------------------------------------------------------
# Gate 5 -- content lints (invariants, not baseline comparisons)
# --------------------------------------------------------------------------


@needs_build
def test_gate5_no_duplicate_ids():
    assert inventory.build_file(BUILT_HTML)["duplicate_ids"] == []


@needs_build
def test_gate5_local_links_resolve():
    """Every local href/src in the built page must exist in _site/."""
    inv = inventory.build_file(BUILT_HTML)
    missing = []
    for url in inv["hrefs"] + inv["srcs"]:
        if url.startswith(("http://", "https://", "//", "#", "mailto:", "data:")):
            continue
        target = SITE / url.lstrip("/").split("?", 1)[0].split("#", 1)[0]
        if not target.exists():
            missing.append(url)
    assert not missing, "unresolved local links:\n" + "\n".join(sorted(missing))


@needs_build
def test_gate5_no_build_output_committed():
    """Generated paths must not appear as tracked files.

    The whole anti-drift design rests on index.html and GraemeBlair-CV.tex not
    existing in any branch. If one gets committed, someone will edit it and
    their edit will be silently discarded on the next build.
    """
    tracked = subprocess.run(
        ["git", "ls-files", "index.html", "GraemeBlair-CV.tex", "GraemeBlair-CV.pdf"],
        cwd=REPO,
        capture_output=True,
        text=True,
    ).stdout.split()
    assert not tracked, f"generated files are tracked in git: {tracked}"
