"""Pre-registered, deliberate deviations from the frozen baseline.

The acceptance suite compares the built site against `baseline/`, which is a
byte-for-byte snapshot of the hand-written site at the commit recorded in
`baseline/COMMIT`. Any difference fails -- unless it is listed here.

The rule: a deviation gets an entry BEFORE the change lands, with a reason a
reader can evaluate. Nothing is fixed silently. Several of these are visible
behavior changes, not cosmetic cleanups, and the owner has to agree to each one.

Each entry is (kind, key, reason):
  kind  "id" | "citation" | "href" | "src" | "toggle"  -- Gate 1, exact match
        "text"                                         -- Gate 2 and the CV
                                                          source, substring match
  key   the value that differs (a distinctive fragment, for "text")
"""

from __future__ import annotations

EXPECTED_DIFFS: list[tuple[str, str, str]] = [
    (
        "id",
        "listPkgAbstract",
        "VISIBLE BEHAVIOR CHANGE. `listAbstract` was used twice in the baseline "
        "(index.html:340 for the list-experiments paper, :544 for the `list` R "
        "package), so the Software tab's chevron expanded the Writing tab's "
        "abstract instead of its own. The R package's collapse is renamed; the "
        "paper keeps `listAbstract`. Clicking that chevron now does something "
        "different -- and correct.",
    ),
    # ---- teaching, moved into content/teaching.yml -------------------------
    (
        "text",
        "170A",
        "One course number now feeds both targets. UCLA renumbered PS 179 to "
        "170A; the site had the new number, the CV still had the old one, and "
        "the syllabus PDF (renamed to UCLA_PS170A_Syllabus.pdf) had the old one "
        "while being linked from the line showing the new one. Owner confirmed "
        "170A is current.",
    ),
    (
        "text",
        "Research Design for Social Science",
        "The site abbreviated PS 292B to 'Research Design'; the CV had the full "
        "title. One title now feeds both. Owner confirmed.",
    ),
    (
        "text",
        "240A-B",
        "The site wrote PS 240a/b, the CV 240A-B. One number now feeds both. "
        "Owner confirmed.",
    ),
    (
        "text",
        "Statistical Programming for Social Science",
        "PS 200X was the only course on the site in sentence case, and carried "
        "a stray trailing period. Titles are stored in sentence case and "
        "title-cased for the site, so it now matches its neighbours.",
    ),
    (
        "text",
        "179",
        "The removal side of the PS 179 -> 170A renumbering above. A rename "
        "registers both the old and the new value, so neither side of the diff "
        "passes unexplained.",
    ),
    (
        "href",
        "teaching/UCLA_PS170A_Syllabus.pdf",
        "Syllabus renamed alongside the course renumbering so the filename and "
        "the displayed number agree. A Gate 5 lint enforces that from now on.",
    ),
    (
        "href",
        "teaching/UCLA_PS179_Syllabus.pdf",
        "Replaced by UCLA_PS170A_Syllabus.pdf -- see above.",
    ),
    (
        "text",
        "UCLA_PS170A_Syllabus.pdf",
        "Syllabus renamed alongside the course renumbering.",
    ),
    # The removal side of each teaching rename. Keys are deliberately specific
    # so each retires exactly one old string and cannot whitelist a future edit.
    (
        "text",
        "292B: Research Design (Ph.D.",
        "Removal side of the PS 292B title change.",
    ),
    ("text", "240a/b", "Removal side of the PS 240A-B renumbering."),
    (
        "text",
        "Statistical programming for social science.",
        "Removal side of the PS 200X title-casing.",
    ),
    # LaTeX comments in the teaching block held historical notes. They moved to
    # comments in content/teaching.yml, next to the course they describe,
    # instead of living in generated output. Listed individually rather than as
    # a blanket "%" key, which would whitelist every future comment change.
    ("text", "%. Winter 2017; Winter 2018", "Historical note, moved to teaching.yml."),
    ("text", "% Fall 2016 (as PS 209); Winter 2018", "Historical note, moved to teaching.yml."),
    ("text", "%Fall 2016 -- Winter 2017", "Historical note, moved to teaching.yml."),
    ("text", "% Politics 572 (Preceptor).", "Historical note, moved to teaching.yml."),
]


def is_expected(kind: str, key: str) -> bool:
    return any(k == kind and v == key for k, v, _ in EXPECTED_DIFFS)


def unexplained_diff_lines(diff: str) -> list[str]:
    """Diff lines not covered by a registered "text" entry.

    Substring rather than exact match, because a text change is registered by
    the distinctive fragment that changed, not by the whole surrounding line --
    a diff line carries indentation and neighbouring words that are noise.
    """
    keys = [v for k, v, _ in EXPECTED_DIFFS if k == "text"]
    unexplained = []
    for line in diff.splitlines():
        if not line.startswith(("+", "-")) or line.startswith(("+++", "---")):
            continue
        body = line[1:]
        if not body.strip():
            continue
        if not any(key in body for key in keys):
            unexplained.append(line)
    return unexplained


def reason(kind: str, key: str) -> str | None:
    for k, v, why in EXPECTED_DIFFS:
        if k == kind and v == key:
            return why
    return None


def describe(kind: str, key: str) -> str:
    why = reason(kind, key)
    return f"{kind} {key!r}: {why}" if why else f"{kind} {key!r}: UNREGISTERED"
