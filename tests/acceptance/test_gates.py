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
from expected_diffs import describe, is_expected, unexplained_diff_lines

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


def test_canonicalizer_ignores_bare_layout_wrappers():
    """A moved <div>/<p> wrapper is not a content change; a lost <i> is.

    Regenerating a section reshuffles wrappers, and reporting each one buries
    the text changes that matter. Inline formatting stays in scope because
    losing it changes how the text reads.
    """
    plain = "<div><p>Hello <i>world</i></p></div>"
    rewrapped = "<span><div><p>Hello <i>world</i></p></div></span>"
    assert normalize_html.canonicalize(plain) == normalize_html.canonicalize(rewrapped)

    # A wrapper carrying an attribute this gate keeps is real. `id` is not one
    # of them -- identifiers are Gate 1's business, and it compares them exactly.
    assert normalize_html.canonicalize(plain) != normalize_html.canonicalize(
        '<div role="alert"><p>Hello <i>world</i></p></div>'
    )
    assert normalize_html.canonicalize(plain) == normalize_html.canonicalize(
        '<div id="x"><p>Hello <i>world</i></p></div>'
    )
    assert normalize_html.canonicalize(plain) != normalize_html.canonicalize(
        "<div><p>Hello world</p></div>"
    )
    # An empty <p> is a spacer with real height, so it is still reported.
    assert normalize_html.canonicalize(plain) != normalize_html.canonicalize(
        "<div><p>Hello <i>world</i></p><p></p></div>"
    )


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

    # Toggles are keyed by their target, so a registered id rename covers the
    # control that points at it.
    base_toggles = {tuple(t) for t in base["toggles"]}
    built_toggles = {tuple(t) for t in built["toggles"]}
    for kind_, target in sorted(base_toggles ^ built_toggles):
        if not is_expected("id", target.lstrip("#")):
            problems.append(f"toggle changed: {kind_} -> {describe('id', target.lstrip('#'))}")

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
    unexplained = unexplained_diff_lines(diff)
    assert not unexplained, (
        "prose changed without a registered reason:\n"
        + "\n".join(unexplained)
        + "\n\nAdd a ('text', <fragment>, <why>) entry to expected_diffs.py, or "
        "fix the content."
    )


def _tidy_errors(path: Path) -> set[str]:
    """Tidy's error messages, with line/column stripped so they compare across files."""
    result = subprocess.run(
        ["tidy", "-errors", "-quiet", "-utf8", str(path)],
        capture_output=True,
        text=True,
    )
    return {
        ln.split(" - ", 1)[1].strip()
        for ln in result.stderr.splitlines()
        if " Error: " in ln and " - " in ln
    }


@needs_build
@pytest.mark.skipif(shutil.which("tidy") is None, reason="tidy not installed")
def test_gate2_built_html_introduces_no_new_validity_errors():
    """The built page must not add HTML validity errors the baseline lacks.

    Deliberately a subset check, not "zero errors". The `tidy` shipped with
    macOS predates HTML5 and reports `<main>` and `<figure>` as unrecognized on
    both files; demanding zero would mean either failing forever or teaching the
    test about one machine's tidy vintage. Duplicate ids -- the failure this was
    meant to catch -- are checked directly and more reliably by Gates 1 and 5.
    """
    new = _tidy_errors(BUILT_HTML) - _tidy_errors(BASE_HTML)
    assert not new, "new HTML validity errors:\n" + "\n".join(sorted(new))


# --------------------------------------------------------------------------
# Gate 4 -- the CV
# --------------------------------------------------------------------------


BUILT_TEX = SITE / "GraemeBlair-CV.tex"


@pytest.mark.skipif(not BUILT_TEX.exists(), reason="no _site/GraemeBlair-CV.tex yet")
def test_gate4_cv_source_changes_are_all_registered():
    """Every line of the generated CV source that differs from the baseline
    must be explained by an expected_diffs entry.

    This is the CV's only real protection until CI runs XeLaTeX. It is stronger
    than it looks: the baseline .tex is 550 lines, so a stray escaping bug or a
    dropped section shows up here immediately, in a diff a human can read --
    rather than four minutes later as a subtly wrong PDF nobody proofreads.

    Whitespace-only changes are ignored: the generator reflows the lines it
    owns, and trailing spaces in the hand-written source carry no meaning.
    """
    baseline = (BASELINE / "GraemeBlair-CV.tex").read_text(encoding="utf-8")
    built = BUILT_TEX.read_text(encoding="utf-8")

    import difflib
    import re

    def norm(text: str) -> list[str]:
        out = []
        for line in text.splitlines():
            line = re.sub(r"[ \t]+", " ", line).strip()
            # TeX absorbs space before a line-break macro, so `UCLA \\[.75em]`
            # and `UCLA\\[.75em]` typeset identically. Normalized so reflowing a
            # generated line does not read as a content change. Deliberately
            # narrow -- stripping all whitespace would make `PS 200E` and
            # `PS200E` compare equal, and this gate exists to catch exactly that
            # kind of slip.
            line = re.sub(r" +(\\\\)", r"\1", line)
            # `\\[0.75em]` and `\\[.75em]` are the same length; the
            # hand-written CV used both, 29 times and 85 times respectively.
            # A notation difference, not a content one.
            line = re.sub(r"\[0\.(\d+em\])", r"[.\1", line)
            out.append(line + "\n")
        return out

    diff = "".join(
        difflib.unified_diff(
            norm(baseline), norm(built), fromfile="baseline", tofile="built"
        )
    )
    unexplained = unexplained_diff_lines(diff)
    assert not unexplained, (
        "CV source changed without a registered reason:\n" + "\n".join(unexplained)
    )


@needs_pdf
def test_gate4_cv_page_count():
    import compare_pdf

    assert compare_pdf.page_count(BUILT_PDF) == BASELINE_PAGES


@needs_pdf
def test_gate4_cv_text_matches_baseline():
    import compare_pdf

    diff = compare_pdf.text_diff(BASE_PDF, BUILT_PDF)
    unexplained = unexplained_diff_lines(diff)
    assert not unexplained, (
        "typeset CV changed without a registered reason:\n" + "\n".join(unexplained)
    )


@needs_pdf
@pytest.mark.skipif(shutil.which("pdftoppm") is None, reason="poppler not installed")
def test_gate4_cv_page_images_match_baseline():
    import compare_pdf

    bad = [
        f"page {r['page']}: {r['fraction']:.5%} bbox={r['bbox']}"
        for r in compare_pdf.image_diffs(BASE_PDF, BUILT_PDF)
        if not r.get("skipped") and (r["fraction"] > 0.001 or r["size_mismatch"])
    ]
    assert not bad, "\n".join(bad)


# --------------------------------------------------------------------------
# Gate 5 -- content lints (invariants, not baseline comparisons)
# --------------------------------------------------------------------------


@needs_build
def test_gate5_no_duplicate_ids():
    assert inventory.build_file(BUILT_HTML)["duplicate_ids"] == []


# Built by the macOS XeLaTeX job and dropped into _site/ by CI, so it is absent
# from a plain local `build.py` run. Its presence is asserted separately.
CI_SUPPLIED = {"GraemeBlair-CV.pdf"}


@needs_build
def test_gate5_local_links_resolve():
    """Every local href/src in the built page must exist in _site/."""
    inv = inventory.build_file(BUILT_HTML)
    missing = []
    for url in inv["hrefs"] + inv["srcs"]:
        if url.startswith(("http://", "https://", "//", "#", "mailto:", "data:")):
            continue
        path = url.lstrip("/").split("?", 1)[0].split("#", 1)[0]
        if path in CI_SUPPLIED and not BUILT_PDF.exists():
            continue
        if not (SITE / path).exists():
            missing.append(url)
    assert not missing, "unresolved local links:\n" + "\n".join(sorted(missing))


def test_gate5_syllabus_filenames_match_course_numbers():
    """A course's syllabus filename must contain its number.

    This is the lint that would have caught the PS 179 / POL SCI 170A drift
    years earlier: the site displayed 170A while linking a file called
    UCLA_PS179_Syllabus.pdf, and nothing anywhere objected.
    """
    from sitegen.content import CONTENT, load_one

    teaching = load_one(CONTENT / "teaching.yml")
    problems = []
    for course in teaching["courses"]:
        syllabus = course.get("syllabus")
        if not syllabus:
            continue
        # Case-insensitive, and a two-quarter sequence like 240A-B may be
        # documented by the syllabus for either half (UCLA_PS240a_Fall2016.pdf).
        # Matching only the first segment keeps the check sharp -- 200E still
        # will not accept a file named for 200X.
        wanted = course["number"].split("-")[0].lower()
        if wanted not in syllabus.lower():
            problems.append(f"PS {course['number']} links {syllabus}")
    assert not problems, "syllabus filename does not match course number:\n" + "\n".join(
        problems
    )


def test_gate5_syllabus_files_exist():
    from sitegen.content import CONTENT, load_one
    from sitegen.envs import STATIC

    teaching = load_one(CONTENT / "teaching.yml")
    missing = [
        c["syllabus"]
        for c in teaching["courses"]
        if c.get("syllabus") and not (STATIC / c["syllabus"]).exists()
    ]
    assert not missing, "missing syllabus files:\n" + "\n".join(missing)


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
